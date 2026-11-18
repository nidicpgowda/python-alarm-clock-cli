"""Background scheduler used by the interactive run command."""
import logging
import threading
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from .models import WEEKDAYS
from .service import AlarmService

logger = logging.getLogger(__name__)


class AlarmScheduler:
    def __init__(self, service: AlarmService, on_ring, poll_seconds: float = 0.5):
        self.service = service
        self.on_ring = on_ring
        self.poll_seconds = poll_seconds
        self._stop = threading.Event()
        self._ringing: dict[str, datetime] = {}
        self._last_fired: dict[str, str] = {}
        self._snoozed_until: dict[str, datetime] = {}
        self._lock = threading.RLock()

    def start(self):
        worker = threading.Thread(target=self._run, name="alarm-scheduler", daemon=True)
        worker.start()
        return worker

    def stop(self):
        self._stop.set()

    def snooze(self, alarm_id: str, minutes: int):
        if not 1 <= minutes <= 60:
            raise ValueError("Snooze duration must be between 1 and 60 minutes.")
        with self._lock:
            if alarm_id not in self._ringing:
                raise ValueError(f"Alarm '{alarm_id}' is not currently ringing.")
            self._snoozed_until[alarm_id] = datetime.now(timezone.utc) + timedelta(minutes=minutes)
            self._ringing.pop(alarm_id, None)

    def dismiss(self, alarm_id: str):
        with self._lock:
            if alarm_id not in self._ringing:
                raise ValueError(f"Alarm '{alarm_id}' is not currently ringing.")
            self._ringing.pop(alarm_id, None)
            self._snoozed_until.pop(alarm_id, None)

    def ringing_ids(self):
        with self._lock:
            return list(self._ringing.keys())

    @staticmethod
    def _is_scheduled_now(alarm, local_now: datetime) -> bool:
        if local_now.hour != alarm.hour or local_now.minute != alarm.minute:
            return False
        if alarm.alarm_date:
            return local_now.date().isoformat() == alarm.alarm_date
        if alarm.weekdays:
            return WEEKDAYS[local_now.weekday()] in alarm.weekdays
        return True

    def _run(self):
        while not self._stop.is_set():
            now_utc = datetime.now(timezone.utc)
            try:
                alarms = self.service.list_alarms()
                for alarm in alarms:
                    if not alarm.enabled:
                        continue
                    with self._lock:
                        snooze_due = self._snoozed_until.get(alarm.id)
                        if snooze_due and now_utc >= snooze_due:
                            self._snoozed_until.pop(alarm.id, None)
                            self._ringing[alarm.id] = now_utc
                            self.on_ring(alarm)
                            continue
                        if snooze_due:
                            continue

                    local_now = now_utc.astimezone(ZoneInfo(alarm.timezone))
                    if not self._is_scheduled_now(alarm, local_now):
                        continue

                    occurrence_key = f"{local_now.date().isoformat()}T{alarm.time_text}@{alarm.timezone}"
                    with self._lock:
                        if self._last_fired.get(alarm.id) == occurrence_key:
                            continue
                        self._last_fired[alarm.id] = occurrence_key
                        self._ringing[alarm.id] = now_utc
                    self.on_ring(alarm)
            except Exception:
                logger.exception("Scheduler iteration failed")
            self._stop.wait(self.poll_seconds)
