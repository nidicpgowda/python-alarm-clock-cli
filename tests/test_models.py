import unittest
from alarm_cli.models import Alarm


class AlarmModelTests(unittest.TestCase):
    def test_create_alarm_has_id(self):
        alarm = Alarm.create("Wake up", 7, 30, "Asia/Kolkata")
        self.assertTrue(alarm.id)
        self.assertEqual(alarm.time_text, "07:30")

    def test_rejects_invalid_time(self):
        alarm = Alarm.create("Bad", 25, 0, "Asia/Kolkata")
        with self.assertRaises(ValueError):
            alarm.validate()

    def test_rejects_empty_label(self):
        alarm = Alarm.create(" ", 7, 0, "Asia/Kolkata")
        with self.assertRaises(ValueError):
            alarm.validate()

    def test_json_round_trip(self):
        alarm = Alarm.create("Gym", 6, 15, "Asia/Kolkata", weekdays=("mon", "wed"))
        restored = Alarm.from_dict(alarm.to_dict())
        self.assertEqual(restored, alarm)


if __name__ == "__main__":
    unittest.main()
