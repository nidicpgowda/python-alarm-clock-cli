# Implementation Plan

## Phase 1 — Define behavior
- Agree time format, recurrence rules, timezone behavior, and persistence format.
- Define functional and non-functional requirements.
- Document assumptions and exclusions.

## Phase 2 — Domain model
- Implement `Alarm`.
- Add validation and serialization.
- Unit-test invalid and valid alarm data.

## Phase 3 — Persistence and use cases
- Implement JSON repository.
- Add service operations: create, list, delete, enable, disable.
- Test repository round-trip and service behavior.

## Phase 4 — Scheduling
- Implement next-occurrence calculations.
- Add timezone-aware daily, weekly, and one-time behavior.
- Implement monitor thread, duplicate-fire guard, snooze, and dismiss.
- Test calculations separately from real-time waiting.

## Phase 5 — CLI
- Add argparse commands and helpful usage text.
- Add interactive monitor commands.
- Add consistent error handling.

## Phase 6 — Quality and delivery
- Run automated tests and manual smoke tests.
- Review code readability, naming, and module boundaries.
- Update README and architecture decisions.
- Create focused Git commits.
- Push the repository to GitHub.
- Record a short walkthrough video.

## Definition of done
- Requirements and assumptions are documented.
- CLI commands work from a clean environment.
- Automated tests pass.
- No database, web server, or frontend is present.
- README contains setup, usage, architecture, limitations, and tests.
- Git history communicates the implementation progression.
