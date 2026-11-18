# Interview Walkthrough Video (5–7 minutes)

## 0:00–0:40 — Problem and scope
"I built a terminal-based alarm clock in Python. The prompt was open-ended, so I first defined functional and non-functional requirements. I intentionally kept it local and dependency-light: no web UI, no database, and no external service."

## 0:40–1:40 — Requirements and decisions
"Users can create daily, one-time, and weekday alarms; list, enable, disable, and delete them; and snooze or dismiss an active alarm. Alarm definitions are stored in JSON. I chose JSON because this is a small local configuration tool and the assignment excludes databases."

## 1:40–2:40 — Architecture
"CLI parsing is separate from application logic. The Alarm model owns validation and serialization. AlarmService handles use cases and next-occurrence calculations. JsonAlarmRepository owns persistence. AlarmScheduler runs separately and calls a notification callback. This makes business rules testable without invoking the terminal."

## 2:40–4:10 — Demo
Show:
1. `alarm --help`
2. Add a daily alarm.
3. Add a weekday alarm.
4. List alarms.
5. Disable and enable an alarm.
6. Delete an alarm.
7. Start `alarm run`; demonstrate `list`, `snooze`, and `dismiss` using a near-future test alarm if practical.

## 4:10–5:10 — Testing and quality
"Tests cover model validation, serialization, service operations, and timezone-aware occurrence calculation. I use only the Python standard library. I also documented operational limitations, such as the monitor needing to remain active and snooze state being transient."

## 5:10–6:10 — Trade-offs and next steps
"Polling is portable and simple for a small number of alarms, though not a hard real-time scheduler. JSON is simple but doesn't coordinate concurrent processes. For production, I'd consider file locking, persisted snoozes, OS notifications, and a clock abstraction for deterministic scheduler integration tests."

## 6:10–6:40 — Git history
Show focused commits and explain how each commit represents one logical change.

## Recording tips
- Record the terminal and editor at readable zoom.
- Use a temporary test JSON file so personal alarms are not exposed.
- Avoid showing tokens, email, personal paths, or unrelated desktop notifications.
- Keep the demo deterministic; don't rely on waiting many minutes for a real alarm.
