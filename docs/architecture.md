# Architecture

Single file, `claude-keepalive.py`. No dependencies.

## Overview

A loop launches `claude` in a pseudo-terminal, proxies stdin/stdout so the TUI
works, and scans the output stream for the session-limit banner. On a hit it
waits until the reset time and relaunches, resuming the same session.

## Components

- `run_claude(command)` — `pty.fork()`s the child, puts the real terminal in
  raw mode, and shuttles bytes between stdin, the PTY, and stdout with
  `select`. Strips ANSI escapes from a rolling buffer to match on plain text.
- `wait_until(reset)` — parses the `H:MMam/pm` reset string and `time.sleep()`s
  until it (rolling to the next day if already past), plus a small margin.
- `main()` — argument parsing (`--resume`), signal forwarding, and the
  detect → wait → resume loop.

## Data flow

`stdin → PTY → claude`, `claude → PTY → stdout` (tee'd into a rolling buffer).
The buffer is regex-scanned for `You've hit your session limit`, the reset
time (`RESET_PATTERN`), and the resume id (`RESUME_PATTERN`).

## Decisions

- **PTY over pipes:** the Claude TUI needs a real terminal; pipes would break
  rendering and input.
- **Ignore the first `IGNORE_INITIAL_BYTES`:** avoids false positives from the
  startup banner / help text.
- **Stdlib only:** keeps it a zero-install, copy-and-run script.
