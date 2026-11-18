
"""Background scheduler used by the interactive run command."""

import logging
import threading
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .models import WEEKDAYS
from .service import AlarmService

logger = logging.getLogger(__name__)


class AlarmScheduler:

    def __init__(
        self,
        service: AlarmService,
        on_ring,
        poll_seconds: float = 0.5,
        clock=None
    ):
        self.service = service
        self.on_ring = on_ring
        self.poll_seconds = poll_seconds

        # Injected clock makes time-dependent behavior testable.
        self.clock = clock or (
            lambda: datetime.now(timezone.utc)
        )

        self._stop = threading.Event()
        self._ringing: dict[str, datetime] = {}
        self._last_fired: dict[str, str] = {}
        self._snoozed_until: dict[str, datetime] = {}
        self._lock = threading.RLock()

    def start(self):
        """Start the background scheduler thread."""
        worker = threading.Thread(
            target=self._run,
            name="alarm-scheduler",
            daemon=True
        )
        worker.start()
        return worker

    def stop(self):
        """Signal the scheduler thread to stop."""
        self._stop.set()

    def snooze(self, alarm_id: str, minutes: int):
        """Snooze an actively ringing alarm."""
        if not 1 <= minutes <= 60:
            raise ValueError(
                "Snooze duration must be between 1 and 60 minutes."
            )

        with self._lock:
            if alarm_id not in self._ringing:
                raise ValueError(
                    f"Alarm '{alarm_id}' is not currently ringing."
                )

            self._snoozed_until[alarm_id] = (
                self.clock() + timedelta(minutes=minutes)
            )

            self._ringing.pop(alarm_id, None)

    def dismiss(self, alarm_id: str):
        """Dismiss an actively ringing alarm."""
        with self._lock:
            if alarm_id not in self._ringing:
                raise ValueError(
                    f"Alarm '{alarm_id}' is not currently ringing."
                )

            self._ringing.pop(alarm_id, None)
            self._snoozed_until.pop(alarm_id, None)

    def ringing_ids(self):
        """Return IDs of currently ringing alarms."""
        with self._lock:
            return list(self._ringing.keys())

    @staticmethod
    def _is_scheduled_now(alarm, local_now: datetime) -> bool:
        """Check whether an alarm matches the current local time."""
        if (
            local_now.hour != alarm.hour
            or local_now.minute != alarm.minute
        ):
            return False

        if alarm.alarm_date:
            return local_now.date().isoformat() == alarm.alarm_date

        if alarm.weekdays:
            return WEEKDAYS[local_now.weekday()] in alarm.weekdays

        return True

    def _process_alarms(self, now_utc: datetime):
        """
        Process scheduled and snoozed alarms for a given UTC timestamp.

        Separated from the background loop to support deterministic tests.
        """
        alarms = self.service.list_alarms()

        for alarm in alarms:
            if not alarm.enabled:
                continue

            should_ring = False

            with self._lock:
                snooze_due = self._snoozed_until.get(alarm.id)

                # Check whether a snoozed alarm is ready to ring again.
                if snooze_due:
                    if now_utc >= snooze_due:
                        self._snoozed_until.pop(alarm.id, None)
                        self._ringing[alarm.id] = now_utc
                        should_ring = True
                    else:
                        continue

                else:
                    # Convert UTC time into the alarm's configured timezone.
                    local_now = now_utc.astimezone(
                        ZoneInfo(alarm.timezone)
                    )

                    if not self._is_scheduled_now(alarm, local_now):
                        continue

                    # Prevent the same occurrence from triggering repeatedly.
                    occurrence_key = (
                        f"{local_now.date().isoformat()}"
                        f"T{alarm.time_text}@{alarm.timezone}"
                    )

                    if (
                        self._last_fired.get(alarm.id)
                        == occurrence_key
                    ):
                        continue

                    self._last_fired[alarm.id] = occurrence_key
                    self._ringing[alarm.id] = now_utc
                    should_ring = True

            # Execute the callback outside the scheduler lock.
            if should_ring:
                self.on_ring(alarm)

    def _run(self):
        """Background loop that periodically checks alarms."""
        while not self._stop.is_set():
            try:
                now_utc = self.clock()
                self._process_alarms(now_utc)

            except Exception:
                logger.exception("Scheduler iteration failed")

            self._stop.wait(self.poll_seconds)
