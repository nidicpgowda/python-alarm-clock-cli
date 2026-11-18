"""Command-line interface."""
import argparse
import logging
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import Alarm, WEEKDAYS
from .repository import JsonAlarmRepository
from .service import AlarmService
from .scheduler import AlarmScheduler

DEFAULT_FILE = Path.home() / ".alarm-cli" / "alarms.json"


def build_parser():
    parser = argparse.ArgumentParser(prog="alarm", description="A simple terminal alarm clock.")
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE,
                        help=f"alarm JSON file (default: {DEFAULT_FILE})")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="create an alarm")
    add.add_argument("--time", required=True, help="24-hour time, HH:MM")
    add.add_argument("--label", default="Alarm")
    add.add_argument("--timezone", default="Asia/Kolkata", help="IANA timezone")
    add.add_argument("--date", dest="alarm_date", help="one-time date, YYYY-MM-DD")
    add.add_argument("--days", help="recurring days, e.g. mon,wed,fri")
    add.add_argument("--snooze", type=int, default=5, help="snooze duration in minutes")

    sub.add_parser("list", help="list configured alarms")

    delete = sub.add_parser("delete", help="delete an alarm")
    delete.add_argument("id")

    enable = sub.add_parser("enable", help="enable an alarm")
    enable.add_argument("id")

    disable = sub.add_parser("disable", help="disable an alarm")
    disable.add_argument("id")

    sub.add_parser("run", help="start the interactive alarm monitor")
    return parser


def parse_alarm_time(value):
    try:
        parsed = datetime.strptime(value, "%H:%M")
        if parsed.strftime("%H:%M") != value:
            raise ValueError
        return parsed.hour, parsed.minute
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Time must be in HH:MM 24-hour format.") from exc


def print_alarms(alarms):
    if not alarms:
        print("No alarms configured.")
        return
    print(f"{'ID':8} {'TIME':5} {'STATUS':8} {'SCHEDULE':20} {'TIMEZONE':22} LABEL")
    print("-" * 90)
    for a in alarms:
        schedule = a.alarm_date or (",".join(a.weekdays) if a.weekdays else "Daily")
        status = "enabled" if a.enabled else "disabled"
        print(f"{a.id:8} {a.time_text:5} {status:8} {schedule:20} {a.timezone:22} {a.label}")


def ring_alarm(alarm):
    print("\n" + "=" * 55, flush=True)
    print(f"  ALARM: {alarm.label}  [{alarm.id}]", flush=True)
    print(f"  Scheduled time: {alarm.time_text} ({alarm.timezone})", flush=True)
    print("  Terminal bell: \a", flush=True)
    print("=" * 55, flush=True)
    try:
        if os.name == "nt":
            import winsound
            winsound.Beep(1000, 700)
    except (ImportError, RuntimeError):
        pass


def run_monitor(service):
    scheduler = AlarmScheduler(service, ring_alarm)
    worker = scheduler.start()
    print("Alarm monitor running. Commands: list | snooze ID [MINUTES] | dismiss ID | quit")
    try:
        while True:
            command = input("alarm> ").strip().split()
            if not command:
                continue
            action = command[0].lower()
            if action == "quit":
                break
            if action == "list":
                print_alarms(service.list_alarms())
            elif action == "snooze" and len(command) in (2, 3):
                alarm_id = command[1]
                alarms = {a.id: a for a in service.list_alarms()}
                if alarm_id not in alarms:
                    print(f"Unknown alarm ID: {alarm_id}")
                    continue
                minutes = int(command[2]) if len(command) == 3 else alarms[alarm_id].snooze_minutes
                scheduler.snooze(alarm_id, minutes)
                print(f"Alarm {alarm_id} snoozed for {minutes} minutes.")
            elif action == "dismiss" and len(command) == 2:
                scheduler.dismiss(command[1])
                print(f"Alarm {command[1]} dismissed.")
            else:
                print("Unknown command. Use: list | snooze ID [MINUTES] | dismiss ID | quit")
    except (KeyboardInterrupt, EOFError):
        print("\nStopping alarm monitor.")
    finally:
        scheduler.stop()
        worker.join(timeout=2)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(message)s")
    repository = JsonAlarmRepository(args.file)
    service = AlarmService(repository)

    try:
        if args.command == "add":
            hour, minute = parse_alarm_time(args.time)
            days = tuple(day.strip().lower() for day in args.days.split(",")) if args.days else ()
            alarm = Alarm.create(args.label, hour, minute, args.timezone,
                                 args.alarm_date, days, args.snooze)
            service.add_alarm(alarm)
            print(f"Created alarm {alarm.id}: {alarm.label} at {alarm.time_text} ({alarm.timezone})")
        elif args.command == "list":
            print_alarms(service.list_alarms())
        elif args.command == "delete":
            service.delete_alarm(args.id)
            print(f"Deleted alarm {args.id}.")
        elif args.command == "enable":
            service.set_enabled(args.id, True)
            print(f"Enabled alarm {args.id}.")
        elif args.command == "disable":
            service.set_enabled(args.id, False)
            print(f"Disabled alarm {args.id}.")
        elif args.command == "run":
            run_monitor(service)
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
