
import unittest
from datetime import datetime, timedelta, timezone

from alarm_cli.models import Alarm
from alarm_cli.scheduler import AlarmScheduler


class FakeService:
    def __init__(self, alarms):
        self.alarms = alarms

    def list_alarms(self):
        return self.alarms


class SnoozeTests(unittest.TestCase):

    def setUp(self):
        self.now = datetime(
            2026, 11, 18, 1, 30,
            tzinfo=timezone.utc
        )

        self.alarm = Alarm.create(
            "Wake up",
            7,
            0,
            "Asia/Kolkata"
        )

        self.notifications = []

        self.service = FakeService([self.alarm])

        self.scheduler = AlarmScheduler(
            self.service,
            on_ring=lambda alarm: self.notifications.append(alarm.id),
            clock=lambda: self.now
        )

    def test_snooze_sets_correct_expiry_time(self):
        self.scheduler._ringing[self.alarm.id] = self.now

        self.scheduler.snooze(self.alarm.id, 5)

        expected = self.now + timedelta(minutes=5)

        self.assertEqual(
            self.scheduler._snoozed_until[self.alarm.id],
            expected
        )

        self.assertNotIn(
            self.alarm.id,
            self.scheduler.ringing_ids()
        )

    def test_snooze_accepts_minimum_duration(self):
        self.scheduler._ringing[self.alarm.id] = self.now

        self.scheduler.snooze(self.alarm.id, 1)

        self.assertEqual(
            self.scheduler._snoozed_until[self.alarm.id],
            self.now + timedelta(minutes=1)
        )

    def test_snooze_accepts_maximum_duration(self):
        self.scheduler._ringing[self.alarm.id] = self.now

        self.scheduler.snooze(self.alarm.id, 60)

        self.assertEqual(
            self.scheduler._snoozed_until[self.alarm.id],
            self.now + timedelta(minutes=60)
        )

    def test_snooze_rejects_invalid_duration(self):
        self.scheduler._ringing[self.alarm.id] = self.now

        for minutes in (0, 61):
            with self.subTest(minutes=minutes):
                with self.assertRaises(ValueError):
                    self.scheduler.snooze(
                        self.alarm.id,
                        minutes
                    )

    def test_snooze_requires_alarm_to_be_ringing(self):
        with self.assertRaisesRegex(
            ValueError,
            "not currently ringing"
        ):
            self.scheduler.snooze(self.alarm.id, 5)

    def test_alarm_rings_again_after_snooze_expires(self):
        self.scheduler._ringing[self.alarm.id] = self.now

        self.scheduler.snooze(self.alarm.id, 5)

        future_time = self.now + timedelta(minutes=5)

        self.scheduler._process_alarms(future_time)

        self.assertIn(
            self.alarm.id,
            self.scheduler.ringing_ids()
        )

        self.assertEqual(
            self.notifications,
            [self.alarm.id]
        )

        self.assertNotIn(
            self.alarm.id,
            self.scheduler._snoozed_until
        )

    def test_dismiss_removes_active_alarm(self):
        self.scheduler._ringing[self.alarm.id] = self.now

        self.scheduler.dismiss(self.alarm.id)

        self.assertNotIn(
            self.alarm.id,
            self.scheduler.ringing_ids()
        )

    def test_dismiss_clears_snooze_state(self):
        self.scheduler._ringing[self.alarm.id] = self.now

        self.scheduler._snoozed_until[self.alarm.id] = (
            self.now + timedelta(minutes=5)
        )

        self.scheduler.dismiss(self.alarm.id)

        self.assertNotIn(
            self.alarm.id,
            self.scheduler._snoozed_until
        )

    def test_dismiss_prevents_same_occurrence_from_ringing_again(self):
        scheduled_time = datetime(
            2026, 11, 18, 7, 0,
            tzinfo=timezone.utc
        )

        self.alarm.hour = 12
        self.alarm.minute = 30

        # 07:00 UTC is 12:30 in Asia/Kolkata.
        self.scheduler._process_alarms(scheduled_time)

        self.assertEqual(len(self.notifications), 1)

        self.scheduler.dismiss(self.alarm.id)

        self.scheduler._process_alarms(scheduled_time)

        self.assertEqual(len(self.notifications), 1)


if __name__ == "__main__":
    unittest.main()
