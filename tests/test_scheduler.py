import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from alarm_cli.models import Alarm
from alarm_cli.scheduler import AlarmScheduler


class SchedulerMatchingTests(unittest.TestCase):
    def test_daily_alarm_matches_configured_local_minute(self):
        alarm = Alarm.create("Wake", 7, 30, "Asia/Kolkata")
        now = datetime(2026, 11, 18, 7, 30, 10, tzinfo=ZoneInfo("Asia/Kolkata"))
        self.assertTrue(AlarmScheduler._is_scheduled_now(alarm, now))

    def test_weekly_alarm_only_matches_selected_weekday(self):
        alarm = Alarm.create("Work", 9, 0, "Asia/Kolkata", weekdays=("thu",))
        wednesday = datetime(2026, 11, 18, 9, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
        thursday = datetime(2026, 11, 19, 9, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
        self.assertFalse(AlarmScheduler._is_scheduled_now(alarm, wednesday))
        self.assertTrue(AlarmScheduler._is_scheduled_now(alarm, thursday))

    def test_one_time_alarm_matches_only_configured_date(self):
        alarm = Alarm.create("Meeting", 10, 0, "Asia/Kolkata", alarm_date="2026-11-19")
        correct = datetime(2026, 11, 19, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
        wrong = datetime(2026, 11, 20, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
        self.assertTrue(AlarmScheduler._is_scheduled_now(alarm, correct))
        self.assertFalse(AlarmScheduler._is_scheduled_now(alarm, wrong))


if __name__ == "__main__":
    unittest.main()
