# Suggested Git Commit Sequence

Create these commits as you implement, rather than committing the entire finished project once.

1. `chore: initialize Python CLI project structure`
2. `feat: add alarm domain model and validation`
3. `feat: add JSON alarm repository`
4. `feat: implement alarm management service`
5. `feat: calculate timezone-aware alarm occurrences`
6. `feat: add background alarm scheduler`
7. `feat: add CLI commands for alarm management`
8. `feat: support snooze and dismiss in monitor`
9. `test: cover alarm model and service behavior`
10. `docs: add requirements architecture and usage guide`

Before each commit:
- Run relevant tests.
- Review `git diff`.
- Keep unrelated changes out of the commit.
- Use imperative, descriptive commit messages.

Do not fabricate a commit history after the fact. If the project is already implemented, make honest commits based on real reviewable changes.
