# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1](https://github.com/fabiocicerchia/claude-keepalive/compare/v0.1.0...v0.1.1) (2026-07-30)


### Bug Fixes

* make limit detection and auto-resume work reliably ([#6](https://github.com/fabiocicerchia/claude-keepalive/issues/6)) ([067f228](https://github.com/fabiocicerchia/claude-keepalive/commit/067f2287504b5863ffce5e0ad01b106085942d2f))

## [Unreleased]

### Fixed

- Reset times without minutes (e.g. `resets 3am`) are now parsed; previously
  the wrapper exited instead of waiting.
- Detect all known limit-banner wordings (session/usage/5-hour limit, curly
  or straight apostrophe), not just one phrase.
- Keep reading briefly after the limit phrase so a reset time arriving in a
  later output chunk isn't lost.
- Only restart when the limit banner was actually seen; a normal exit no
  longer risks a spurious wait-and-restart, and the child's real exit code
  is propagated.
- Reap the child after the limit kill (no more zombies) and close the PTY fd
  on each relaunch (no fd leak); escalate to SIGKILL if `claude` ignores
  SIGTERM.
- `Ctrl-C` is now forwarded to `claude` (cancel / double-press to quit)
  instead of killing it outright; during the wait, `Ctrl-C`/SIGTERM stop the
  wrapper cleanly.
- Propagate the real terminal size to the PTY and follow `SIGWINCH`, so the
  TUI no longer renders at 80x24.
- Fail with a clear message when stdin isn't a TTY or `claude` isn't on
  `PATH`, instead of a traceback.

### Changed

- Skip the initial-output detection gate on fresh sessions (it exists to
  ignore replayed history on resume), so a session already at its limit is
  detected immediately.
- Wait a 30-minute fallback and retry when the banner has no parseable reset
  time, instead of giving up.
- Add a 60s margin after the advertised reset time before resuming.

### Added

- Test suite (`make test`, stdlib `unittest`): parsing/detection units plus
  PTY end-to-end tests against a fake `claude`.

## [0.1.0]

### Added

- Transparent PTY wrapper around the `claude` CLI.
- Detects the session-limit message, parses the reset time, and waits it out.
- Resumes the same session (`--resume`, falling back to `--continue`) after the wait.

[Unreleased]: https://github.com/fabiocicerchia/claude-keepalive/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fabiocicerchia/claude-keepalive/releases/tag/v0.1.0
