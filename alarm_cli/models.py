"""Domain models for the alarm clock."""
from dataclasses import dataclass, asdict
from datetime import date, datetime, time
from typing import Optional
from uuid import uuid4

WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


@dataclass
class Alarm:
    id: str
    label: str
    hour: int
    minute: int
    timezone: str
    enabled: bool = True
    alarm_date: Optional[str] = None
    weekdays: tuple[str, ...] = ()
    snooze_minutes: int = 5

    @classmethod
    def create(
        cls, label: str, hour: int, minute: int, timezone: str,
        alarm_date: Optional[str] = None, weekdays: tuple[str, ...] = (),
        snooze_minutes: int = 5
    ) -> "Alarm":
        return cls(
            id=uuid4().hex[:8], label=label, hour=hour, minute=minute,
            timezone=timezone, alarm_date=alarm_date,
            weekdays=tuple(weekdays), snooze_minutes=snooze_minutes
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["weekdays"] = list(self.weekdays)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Alarm":
        data = dict(data)
        data["weekdays"] = tuple(data.get("weekdays", ()))
        return cls(**data)

    def validate(self) -> None:
        if not self.label.strip():
            raise ValueError("Alarm label cannot be empty.")
        if not 0 <= self.hour <= 23 or not 0 <= self.minute <= 59:
            raise ValueError("Alarm time must be between 00:00 and 23:59.")
        if self.snooze_minutes < 1 or self.snooze_minutes > 60:
            raise ValueError("Snooze duration must be between 1 and 60 minutes.")
        invalid = set(self.weekdays) - set(WEEKDAYS)
        if invalid:
            raise ValueError(f"Invalid weekdays: {', '.join(sorted(invalid))}")
        if self.alarm_date:
            try:
                date.fromisoformat(self.alarm_date)
            except ValueError as exc:
                raise ValueError("Date must use YYYY-MM-DD format.") from exc
        if self.alarm_date and self.weekdays:
            raise ValueError("Choose either a specific date or recurring weekdays, not both.")

    @property
    def time_text(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}"
