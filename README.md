# Alarm CLI

A terminal-only alarm clock built with Python 3.11+. It supports one-time, daily, and weekday-recurring alarms, JSON file persistence, timezone-aware scheduling, snooze, dismiss, and enable/disable operations.

## Design goals

- CLI only: no web UI, frontend, server, or database.
- Standard-library-first implementation.
- Keep domain rules independent from command parsing.
- Persist configuration in a local JSON file.
- Make scheduling calculations independently testable.

## Requirements

- Python 3.11+
- No third-party runtime dependencies

## Setup

```bash
git clone <your-repository-url>
cd alarm-cli
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -e .
```

You can also run without installing the console entry point:

```bash
python -m alarm_cli.cli --help
```

## Usage

Create a daily alarm:

```bash
alarm add --time 07:00 --label "Wake up" --timezone Asia/Kolkata
```

Create a one-time alarm:

```bash
alarm add --time 18:30 --date 2026-11-20 --label "Appointment"
```

Create a recurring weekday alarm:

```bash
alarm add --time 08:15 --days mon,tue,wed,thu,fri --label "Work"
```

List, disable, enable, or delete:

```bash
alarm list
alarm disable <alarm-id>
alarm enable <alarm-id>
alarm delete <alarm-id>
```

Start the monitor:

```bash
alarm run
```

While the monitor is running:

```text
list
snooze <alarm-id>
snooze <alarm-id> 10
dismiss <alarm-id>
quit
```

The default data file is `~/.alarm-cli/alarms.json`. Override it with `--file ./data/alarms.json` (place global options before the command).

## Architecture

```text
CLI / argparse
     |
     v
AlarmService -------------- AlarmScheduler
     |                            |
     v                            v
Alarm domain model          Ring callback
     |
     v
JsonAlarmRepository
     |
     v
Local JSON file
```

### Responsibilities

- `models.py`: Alarm entity, validation, serialization.
- `repository.py`: JSON file read/write and atomic replacement.
- `service.py`: use cases and timezone-aware next-occurrence calculation.
- `scheduler.py`: background polling, duplicate-fire guard, snooze tracking.
- `cli.py`: command parsing, user interaction, and terminal notification.

## Key engineering decisions

1. **JSON instead of a database:** the assignment explicitly excludes databases. JSON is sufficient for a small local configuration dataset and is human-readable.
2. **Standard library:** minimizes installation friction and dependency risk.
3. **Timezone-aware scheduling:** each alarm stores an IANA timezone; calculations are performed in that timezone rather than assuming the machine's local timezone.
4. **Separation of concerns:** CLI, domain/service logic, persistence, and scheduling are separate modules.
5. **Atomic file replacement:** save to a temporary file and replace the target to reduce the chance of a partially written configuration.
6. **Polling interval:** a half-second wait is simple and portable for a small CLI workload. It avoids a tight CPU-consuming loop.
7. **In-memory runtime state:** ringing and snooze state are transient; alarm definitions persist. Restarting the monitor clears active snoozes.

## Known limitations / future improvements

- The monitor must remain running for alarms to trigger.
- Notifications are terminal bell/text; Windows additionally attempts a short beep. Desktop notifications and configurable audio are intentionally excluded.
- The scheduler is designed for a single running monitor process. Concurrent processes editing the same JSON file are not coordinated.
- One-time alarms remain in the file after they pass; users can delete them manually.
- Snooze state is in memory and is lost if the process exits.
- Daylight-saving transitions follow the host's IANA timezone database behavior. Ambiguous/nonexistent local times need an explicit product policy for a production-grade scheduler.

## Testing

```bash
python -m unittest discover -s tests -v
```

## Quality checklist

- [ ] Run tests on Python 3.11+
- [ ] Run CLI help and smoke-test add/list/delete
- [ ] Test invalid time, timezone, date, and weekday input
- [ ] Test monitor, snooze, dismiss, and Ctrl+C
- [ ] Review formatting, naming, and error messages
- [ ] Confirm no secrets or local alarm data are committed
