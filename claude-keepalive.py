#!/usr/bin/env python3
"""Keep a Claude Code session alive across usage-limit resets.

Wraps the `claude` CLI in a PTY, watches its output for the usage/session
limit banner, sleeps until the advertised reset time, then relaunches with
`--resume <id>` (falling back to `--continue`) so the conversation picks up
where it left off.
"""

import argparse
import fcntl
import os
import pty
import re
import select
import signal
import sys
import termios
import time
import tty
from datetime import datetime, timedelta

BUFFER_SIZE = 4096
IGNORE_INITIAL_BYTES = 8192
LIMIT_DRAIN_SECONDS = 2.0
RESET_MARGIN_SECONDS = 60
FALLBACK_WAIT_SECONDS = 30 * 60

# Wording differs across claude versions and limit types; compare lowercase.
LIMIT_PHRASES = (
    "you've hit your session limit",
    "you've hit your usage limit",
    "you've reached your usage limit",
    "claude usage limit reached",
    "5-hour limit reached",
    "session limit reached",
)

ANSI_PATTERN = re.compile(
    rb"\x1b\[[0-?]*[ -/]*[@-~]"  # CSI (colors, cursor movement)
    rb"|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)?"  # OSC (window title)
)
RESET_PATTERN = re.compile(
    r"(?:resets|will reset)\s*(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)",
    re.IGNORECASE,
)
RESUME_PATTERN = re.compile(
    r"claude --resume ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
)

child_pid = None
child_fd = None


def forward_signal(sig, frame):
    if child_pid is None:
        # No child (e.g. sleeping until the reset): stop the wrapper itself.
        raise SystemExit(128 + sig)

    try:
        os.kill(child_pid, sig)
    except ProcessLookupError:
        pass


def sync_winsize(signum=None, frame=None):
    if child_fd is None:
        return

    try:
        size = fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, b"\0" * 8)
        fcntl.ioctl(child_fd, termios.TIOCSWINSZ, size)
    except OSError:
        pass


def write_all(fd, data):
    while data:
        written = os.write(fd, data)
        data = data[written:]


def strip_ansi(data):
    text = ANSI_PATTERN.sub(b"", data).decode(errors="ignore")
    return text.replace("’", "'")


def found_limit(clean):
    lower = clean.lower()
    return any(phrase in lower for phrase in LIMIT_PHRASES)


def parse_reset(clean):
    match = RESET_PATTERN.search(clean)

    if not match:
        return None

    hour, minute, meridiem = match.groups()

    if not 1 <= int(hour) <= 12 or int(minute or 0) > 59:
        return None

    return f"{hour}:{minute or '00'}{meridiem.lower()}"


def seconds_until(reset, now=None):
    # Deliberately naive/local: `reset` is a wall-clock time parsed from
    # Claude CLI's own message (shown in the user's local time), so `now`
    # must be local too for the comparison below to mean anything.
    now = now or datetime.now()  # noqa: DTZ005

    target = datetime.strptime(reset.upper(), "%I:%M%p").replace(  # noqa: DTZ007
        year=now.year, month=now.month, day=now.day
    )

    if target <= now:
        target += timedelta(days=1)

    return int((target - now).total_seconds()) + RESET_MARGIN_SECONDS


def drain(fd, timeout):
    # The reset time can land in a later chunk than the limit phrase; keep
    # forwarding output briefly so it makes it into the buffer.
    data = b""
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        ready, _, _ = select.select([fd], [], [], 0.1)

        if fd not in ready:
            continue

        try:
            chunk = os.read(fd, BUFFER_SIZE)
        except OSError:
            break

        if not chunk:
            break

        write_all(sys.stdout.fileno(), chunk)
        data += chunk

    return data


def reap_child(pid, force=False):
    if force:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

        for _ in range(50):
            try:
                done, status = os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                return 0

            if done:
                return status

            time.sleep(0.1)

        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    try:
        _, status = os.waitpid(pid, 0)
    except ChildProcessError:
        return 0

    return status


def exit_code(status):
    if os.WIFEXITED(status):
        return os.WEXITSTATUS(status)

    if os.WIFSIGNALED(status):
        return 128 + os.WTERMSIG(status)

    return 1


def run_claude(command, ignore_initial=0):
    global child_pid, child_fd

    stdin_fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(stdin_fd)

    pid, fd = pty.fork()

    if pid == 0:
        try:
            os.execvp(command[0], command)
        except OSError:
            os.write(
                2, b"claude-keepalive: cannot launch " + command[0].encode() + b"\r\n"
            )
            os._exit(127)

    child_pid = pid
    child_fd = fd
    buffer = b""
    seen = 0
    limit_hit = False
    watch_stdin = True

    sync_winsize()
    old_winch = signal.signal(signal.SIGWINCH, sync_winsize)

    try:
        tty.setraw(stdin_fd)

        while True:
            fds = [fd, stdin_fd] if watch_stdin else [fd]
            ready, _, _ = select.select(fds, [], [], 0.2)

            if fd in ready:
                try:
                    data = os.read(fd, BUFFER_SIZE)
                except OSError:
                    break

                if not data:
                    break

                write_all(sys.stdout.fileno(), data)
                seen += len(data)

                if seen > ignore_initial:
                    buffer = (buffer + data)[-BUFFER_SIZE:]

                    if found_limit(strip_ansi(buffer)):
                        limit_hit = True
                        buffer = (buffer + drain(fd, LIMIT_DRAIN_SECONDS))[
                            -BUFFER_SIZE:
                        ]
                        break

            if watch_stdin and stdin_fd in ready:
                data = os.read(stdin_fd, 1024)

                if not data:
                    watch_stdin = False
                    continue

                write_all(fd, data)
    finally:
        signal.signal(signal.SIGWINCH, old_winch)
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_settings)

    status = reap_child(pid, force=limit_hit)
    child_pid = None
    child_fd = None

    try:
        os.close(fd)
    except OSError:
        pass

    return exit_code(status), limit_hit, strip_ansi(buffer)


def main():
    parser = argparse.ArgumentParser(
        description="Run claude and auto-resume after usage-limit resets."
    )
    parser.add_argument("--resume", help="Claude session id to resume")
    args = parser.parse_args()

    if not sys.stdin.isatty():
        print("claude-keepalive: stdin must be a TTY", file=sys.stderr)
        return 1

    signal.signal(signal.SIGINT, forward_signal)
    signal.signal(signal.SIGTERM, forward_signal)

    if args.resume:
        command = ["claude", "--resume", args.resume]
    else:
        command = ["claude"]

    resuming = bool(args.resume)

    while True:
        # A resumed session replays history, which can contain an old limit
        # banner; skip the replay before arming detection.
        gate = IGNORE_INITIAL_BYTES if resuming else 0
        code, limit_hit, clean = run_claude(command, ignore_initial=gate)

        if not limit_hit:
            return code

        reset = parse_reset(clean)

        if reset:
            seconds = seconds_until(reset)
            print(f"\nSession limit reached. Resets at {reset}.")
        else:
            seconds = FALLBACK_WAIT_SECONDS
            print("\nSession limit reached; couldn't parse the reset time.")

        until = datetime.now() + timedelta(seconds=seconds)  # noqa: DTZ005
        print(f"Waiting {seconds}s (until ~{until:%H:%M}). Press Ctrl-C to stop.")

        time.sleep(seconds)

        match = RESUME_PATTERN.search(clean)

        if match:
            command = ["claude", "--resume", match.group(1)]
        else:
            command = ["claude", "--continue"]

        resuming = True
        print("Resuming Claude...")


if __name__ == "__main__":
    raise SystemExit(main())
