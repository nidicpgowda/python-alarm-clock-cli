"""Application services and scheduling calculations."""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from .models import Alarm


class AlarmService:
    def __init__(self, repository):
        self.repository = repository

    def list_alarms(self) -> list[Alarm]:
        return sorted(self.repository.load_all(), key=lambda a: (a.hour, a.minute, a.label))

    def add_alarm(self, alarm: Alarm) -> Alarm:
        alarm.validate()
        try:
            ZoneInfo(alarm.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown timezone: {alarm.timezone}") from exc
        alarms = self.repository.load_all()
        alarms.append(alarm)
        self.repository.save_all(alarms)
        return alarm

    def delete_alarm(self, alarm_id: str) -> None:
        alarms = self.repository.load_all()
        remaining = [alarm for alarm in alarms if alarm.id != alarm_id]
        if len(remaining) == len(alarms):
            raise ValueError(f"No alarm found with ID '{alarm_id}'.")
        self.repository.save_all(remaining)

    def set_enabled(self, alarm_id: str, enabled: bool) -> None:
        alarms = self.repository.load_all()
        for alarm in alarms:
            if alarm.id == alarm_id:
                alarm.enabled = enabled
                self.repository.save_all(alarms)
                return
        raise ValueError(f"No alarm found with ID '{alarm_id}'.")

    @staticmethod
    def next_occurrence(alarm: Alarm, now: datetime) -> datetime | None:
        """Return next occurrence in alarm's own timezone, strictly after now."""
        if not alarm.enabled:
            return None
        local_now = now.astimezone(ZoneInfo(alarm.timezone))
        target_time = time(alarm.hour, alarm.minute)

        if alarm.alarm_date:
            target_date = date.fromisoformat(alarm.alarm_date)
            candidate = datetime.combine(target_date, target_time, ZoneInfo(alarm.timezone))
            return candidate if candidate > local_now else None

        if not alarm.weekdays:
            candidate = datetime.combine(local_now.date(), target_time, ZoneInfo(alarm.timezone))
            if candidate <= local_now:
                candidate += timedelta(days=1)
            return candidate

        weekday_numbers = {("mon", 0), ("tue", 1), ("wed", 2), ("thu", 3),
                           ("fri", 4), ("sat", 5), ("sun", 6)}
        selected = {number for name, number in weekday_numbers if name in alarm.weekdays}
        for offset in range(8):
            candidate_date = local_now.date() + timedelta(days=offset)
            if candidate_date.weekday() in selected:
                candidate = datetime.combine(candidate_date, target_time, ZoneInfo(alarm.timezone))
                if candidate > local_now:
                    return candidate
        return None
