# Getting Started

## Prerequisites

- Python 3 (uses stdlib only: `pty`, `termios`, `select`, ...; POSIX/Unix).
- The [`claude`](https://docs.claude.com/en/docs/claude-code) CLI on your `PATH`.

## Setup

```sh
git clone https://github.com/fabiocicerchia/claude-keepalive.git
cd claude-keepalive
```

## Run

```sh
# Fresh session, kept alive across the limit reset:
./claude-keepalive.py

# Resume an existing session:
./claude-keepalive.py --resume <session-id>
```

When the session limit is hit, the wrapper prints the reset time, sleeps until
then (plus a small margin), and resumes automatically — so an overnight limit
doesn't require any manual restart. `Ctrl-C` is forwarded to claude while it
runs (press twice to quit it); during the wait, `Ctrl-C` stops the wrapper.

The wrapper exits with claude's own exit code. Its own refusals are separate:
`64` when stdin is not a TTY (it needs a terminal to wrap) and `127` when the
`claude` binary is not on your `PATH`.

## Test

```sh
make test
```
