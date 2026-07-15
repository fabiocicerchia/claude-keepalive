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
then, and resumes automatically. `Ctrl-C` stops it.
