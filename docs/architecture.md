# Architecture

Single file, `claude-keepalive.py`. No dependencies.

## Overview

A loop launches `claude` in a pseudo-terminal, proxies stdin/stdout so the TUI
works, and scans the output stream for the session-limit banner. On a hit it
waits until the reset time and relaunches, resuming the same session.

## Components

- `run_claude(command, ignore_initial)` — the sequence: put the real terminal
  in raw mode, sync the window size (and follow `SIGWINCH`), `spawn_claude`,
  `pump`, restore the terminal, reap. Returns
  `(exit_code, limit_hit, clean_tail)`.
- `spawn_claude(command)` — `pty.fork()` plus the `execvp`; returns in the
  parent only, since the child either execs or exits `127`.
- `pump(fd, stdin_fd, ignore_initial)` — the `select` loop that shuttles bytes
  between stdin, the PTY, and stdout, via `read_child` and `forward_stdin`.
  Strips ANSI escapes (CSI + OSC) from a rolling buffer to match on plain
  text. Returns `(tail, limit_hit)`.
- `parse_reset(clean)` / `seconds_until(reset)` — parse the `H[:MM]am/pm`
  reset string (`resets …` / `will reset at …`) and compute the sleep,
  rolling to the next day if already past, plus `RESET_MARGIN_SECONDS`.
- `reap_child(pid, force)` — waits for the child; on the limit path sends
  SIGTERM, escalating to SIGKILL after `REAP_POLL_ATTEMPTS` polls, so no
  zombies accumulate. Every send goes through `signal_child`, which tolerates
  the race where the child has already exited.
- `main()` — argument parsing (`--resume`), signal forwarding, and the
  detect → wait → resume loop.

## Data flow

`stdin → PTY → claude` (including `Ctrl-C`, which claude handles itself),
`claude → PTY → stdout` (tee'd into a rolling buffer). The buffer is scanned
for the known limit-banner phrases (`LIMIT_PHRASES`), the reset time
(`RESET_PATTERN`), and the resume id (`RESUME_PATTERN`). After the limit
phrase is seen, output is drained for a couple more seconds so a reset time
arriving in a later chunk still lands in the buffer.

## Decisions

- **PTY over pipes:** the Claude TUI needs a real terminal; pipes would break
  rendering and input.
- **Restart only on a flagged limit:** `run_claude` reports whether the banner
  was actually seen; a normal exit propagates claude's exit code instead of
  re-scanning stale output (which could false-positive on warnings like
  "Approaching usage limit").
- **Ignore the first `IGNORE_INITIAL_BYTES` when resuming:** a resumed session
  replays history that may contain an old limit banner. Fresh sessions skip
  the gate so a session already at its limit is detected immediately.
- **Fallback wait:** if the banner has no parseable reset time, wait
  `FALLBACK_WAIT_SECONDS` and retry rather than giving up.
- **Exit codes:** claude's own exit code is passed through unchanged, so the
  wrapper's own refusals use `sysexits(3)` instead — `64` (`EX_USAGE`) when
  stdin is not a TTY, `127` when `claude` is not on `PATH`, `128 + signal`
  when the wrapper itself is interrupted while waiting.
- **Stdlib only:** keeps it a zero-install, copy-and-run script.
