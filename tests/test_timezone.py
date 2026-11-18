
import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from alarm_cli.models import Alarm
from alarm_cli.service import AlarmService


class FakeRepository:
    def __init__(self):
        self.alarms = []

    def load_all(self):
        return self.alarms

    def save_all(self, alarms):
        self.alarms = alarms


class TimezoneTests(unittest.TestCase):

    def setUp(self):
        self.repository = FakeRepository()
        self.service = AlarmService(self.repository)

    def test_accepts_valid_timezone(self):
        alarm = Alarm.create("Wake", 7, 0, "Asia/Kolkata")

        result = self.service.add_alarm(alarm)

        self.assertEqual(result.timezone, "Asia/Kolkata")

    def test_rejects_invalid_timezone(self):
        alarm = Alarm.create("Wake", 7, 0, "Invalid/Timezone")

        with self.assertRaisesRegex(ValueError, "Unknown timezone"):
            self.service.add_alarm(alarm)

    def test_calculates_next_occurrence_in_configured_timezone(self):
        alarm = Alarm.create("Wake", 7, 0, "Asia/Kolkata")

        now = datetime(
            2026, 11, 18, 1, 0,
            tzinfo=timezone.utc
        )

        result = self.service.next_occurrence(alarm, now)

        expected = datetime(
            2026, 11, 18, 7, 0,
            tzinfo=ZoneInfo("Asia/Kolkata")
        )

        self.assertEqual(result, expected)

    def test_daily_alarm_moves_to_next_day_when_time_has_passed(self):
        alarm = Alarm.create("Wake", 7, 0, "Asia/Kolkata")

        now = datetime(
            2026, 11, 18, 3, 0,
            tzinfo=timezone.utc
        )

        result = self.service.next_occurrence(alarm, now)

        expected = datetime(
            2026, 11, 19, 7, 0,
            tzinfo=ZoneInfo("Asia/Kolkata")
        )

        self.assertEqual(result, expected)

    def test_weekly_alarm_selects_next_matching_weekday(self):
        alarm = Alarm.create(
            "Work",
            9,
            0,
            "Asia/Kolkata",
            weekdays=("thu",)
        )

        now = datetime(
            2026, 11, 18, 6, 0,
            tzinfo=timezone.utc
        )

        result = self.service.next_occurrence(alarm, now)

        expected = datetime(
            2026, 11, 19, 9, 0,
            tzinfo=ZoneInfo("Asia/Kolkata")
        )

        self.assertEqual(result, expected)

    def test_disabled_alarm_has_no_next_occurrence(self):
        alarm = Alarm.create("Wake", 7, 0, "Asia/Kolkata")
        alarm.enabled = False

        now = datetime(
            2026, 11, 18, 1, 0,
            tzinfo=timezone.utc
        )

        result = self.service.next_occurrence(alarm, now)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
