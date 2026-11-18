# Requirements and Acceptance Criteria

## Assumptions

1. The application is a single-user local CLI tool.
2. The monitor process is expected to remain running.
3. The machine's clock and IANA timezone database are trusted.
4. Alarm definitions persist in JSON; active ringing/snooze state is runtime-only.
5. Time input uses 24-hour `HH:MM` format.

## Functional requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| FR-01 | Create | A valid alarm receives a unique ID and is saved. |
| FR-02 | One-time | A date-specific alarm triggers at most once at its scheduled local time. |
| FR-03 | Daily | An alarm without date/weekdays repeats daily. |
| FR-04 | Weekly | A weekday alarm triggers only on selected weekdays. |
| FR-05 | List | User can inspect ID, time, status, schedule, timezone, and label. |
| FR-06 | Delete | Existing alarm is removed; unknown ID returns a useful error. |
| FR-07 | Enable/disable | Disabled alarms are ignored by the scheduler. |
| FR-08 | Snooze | A ringing alarm can be postponed for configured or supplied minutes. |
| FR-09 | Dismiss | A ringing alarm can be stopped. |
| FR-10 | Timezone | Alarm time is interpreted in the selected IANA timezone. |
| FR-11 | Persistence | Alarm definitions survive process restart. |
| FR-12 | Validation | Invalid values are rejected with actionable messages. |

## Non-functional requirements

- Maintainable module boundaries.
- Testable business logic without invoking the CLI.
- No database or network dependency.
- Portable terminal interaction.
- No busy-waiting.
- Human-readable local configuration.
- Clear errors for corrupted configuration.

## Acceptance test scenarios

- Add an alarm and verify it appears in `list`.
- Restart the CLI and verify the alarm remains.
- Disable an alarm and verify it is ignored by the monitor.
- Create a weekday alarm and verify next-occurrence calculation.
- Snooze a ringing alarm and verify it rings again after the requested delay.
- Dismiss a ringing alarm and verify it is no longer active.
- Supply invalid time, date, timezone, weekday, and snooze duration and verify validation.
