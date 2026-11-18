"""JSON-backed persistence. No database is used."""
import json
import logging
from pathlib import Path
from typing import Iterable
from .models import Alarm

logger = logging.getLogger(__name__)


class JsonAlarmRepository:
    def __init__(self, path: Path):
        self.path = path

    def load_all(self) -> list[Alarm]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("Expected a JSON array of alarms.")
            alarms = [Alarm.from_dict(item) for item in raw]
            for alarm in alarms:
                alarm.validate()
            return alarms
        except (json.JSONDecodeError, TypeError, KeyError, ValueError) as exc:
            raise RuntimeError(
                f"Cannot read alarm file '{self.path}': {exc}. "
                "Back up or repair the file before continuing."
            ) from exc

    def save_all(self, alarms: Iterable[Alarm]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [alarm.to_dict() for alarm in alarms]
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary.replace(self.path)
