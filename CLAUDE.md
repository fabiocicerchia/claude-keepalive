# CLAUDE.md

Guidance for Claude Code (and other AI agents) working in this repo.

## Project

`claude-keepalive` is a single-file Python 3 CLI (`claude-keepalive.py`) that
wraps the `claude` binary in a PTY. It forwards the interactive session
through, watches the output for the session-limit message, waits until the
reset time, then relaunches with `--resume <id>` (or `--continue`). Standard
library only — no dependencies.

## Commands

```sh
# run:  ./claude-keepalive.py [--resume <session-id>]
# lint: pre-commit run --all-files   (or: make lint)
# test: make test
```

## Conventions

- Match existing style; don't reformat unrelated code.
- Conventional Commits for messages (see CONTRIBUTING.md).
- Update CHANGELOG.md (`## [Unreleased]`), docs/, and examples/ with behavior changes.
- Never commit secrets; CI runs gitleaks. Keep `.env` out of git.

## Guardrails

- Don't add dependencies without a clear reason; prefer stdlib.
- Don't touch generated files or lockfiles by hand.
- Ask before large refactors or destructive operations.
