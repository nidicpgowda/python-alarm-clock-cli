# Architecture and Design

## Style

A small layered architecture with explicit boundaries:

- Presentation: `cli.py`
- Application/domain services: `service.py`
- Domain model: `models.py`
- Infrastructure: `repository.py`
- Background process: `scheduler.py`

## Main flow: create alarm

1. `argparse` parses command arguments.
2. CLI converts `HH:MM` and weekday arguments.
3. CLI constructs an `Alarm`.
4. `AlarmService` validates the entity and timezone.
5. `JsonAlarmRepository` loads current alarms and persists the new collection.
6. CLI prints the generated alarm ID.

## Main flow: trigger alarm

1. User starts `alarm run`.
2. Scheduler runs in a daemon thread and waits between scans.
3. Scheduler obtains enabled alarms through the service.
4. Service calculates each alarm's next occurrence in its configured timezone.
5. Scheduler checks whether the occurrence is due and guards against duplicate firing.
6. Callback prints the alarm and emits a terminal bell.
7. User enters `snooze`, `dismiss`, or `quit`.

## Scheduling model

Each alarm is evaluated in its own IANA timezone. A daily alarm calculates today's local occurrence; if it has passed, it calculates tomorrow's. A weekly alarm searches the next eight local dates for a selected weekday. A one-time alarm uses its explicit date.

The scheduler uses UTC for elapsed snooze duration and timezone-aware local datetimes for wall-clock alarm schedules.

## Design trade-offs

- **Polling vs OS scheduler:** polling is portable and easy to explain, but is not intended for thousands of alarms or hard real-time guarantees.
- **JSON vs database:** JSON honors the no-database constraint and keeps deployment simple, but does not provide multi-process transactions.
- **Thread vs async:** one background thread is sufficient for this small workload; asyncio would add complexity without a clear benefit.
- **Transient snooze state:** avoids introducing more persistence complexity, but a process restart clears snoozes.

## Reliability considerations

- Use a bounded polling wait to avoid busy loops.
- Use a per-alarm occurrence key to avoid duplicate notifications within one scheduled occurrence.
- Save JSON through a temporary file followed by replacement.
- Log scheduler iteration failures and continue monitoring.
- Validate timezone names and alarm fields before persistence.

## Future design extensions

- Persist snooze state.
- Add OS-level notifications and configurable sound.
- Add a `--once` mode for service managers.
- Add inter-process file locking.
- Add explicit daylight-saving ambiguity policy.
- Add scheduler clock abstraction for deterministic integration tests.
