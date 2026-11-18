import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from alarm_cli.models import Alarm
from alarm_cli.repository import JsonAlarmRepository
from alarm_cli.service import AlarmService


class AlarmServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = JsonAlarmRepository(Path(self.temp.name) / "alarms.json")
        self.service = AlarmService(self.repo)

    def tearDown(self):
        self.temp.cleanup()

    def test_add_and_list_alarm(self):
        alarm = Alarm.create("Wake", 7, 0, "Asia/Kolkata")
        self.service.add_alarm(alarm)
        self.assertEqual(self.service.list_alarms(), [alarm])

    def test_delete_unknown_alarm(self):
        with self.assertRaises(ValueError):
            self.service.delete_alarm("missing")

    def test_next_daily_occurrence_rolls_to_tomorrow(self):
        alarm = Alarm.create("Wake", 7, 0, "Asia/Kolkata")
        now = datetime(2026, 11, 18, 8, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
        result = self.service.next_occurrence(alarm, now)
        self.assertEqual(result.day, 19)
        self.assertEqual(result.hour, 7)

    def test_next_occurrence_for_recurring_day(self):
        alarm = Alarm.create("Work", 9, 0, "Asia/Kolkata", weekdays=("thu",))
        now = datetime(2026, 11, 18, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
        result = self.service.next_occurrence(alarm, now)
        self.assertEqual(result.weekday(), 3)


if __name__ == "__main__":
    unittest.main()
