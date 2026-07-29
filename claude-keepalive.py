#!/usr/bin/env python3

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
RESET_PATTERN = re.compile(r"resets (\d+:\d+)(am|pm)")
RESUME_PATTERN = re.compile(r"claude --resume ([a-f0-9-]+)")

child_pid = None
child_fd = None


def forward_signal(sig, frame):
    if child_pid:
        os.kill(child_pid, sig)


def sync_winsize(*_):
    if not child_fd:
        return

    winsize = fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, b"\0" * 8)

    try:
        fcntl.ioctl(child_fd, termios.TIOCSWINSZ, winsize)
    except OSError:
        pass


def run_claude(command):
    global child_pid, child_fd

    buffer = b""

    try:
        stdin_fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(stdin_fd)
        tty.setraw(stdin_fd)
        pid, fd = pty.fork()

        if pid == 0:
            os.execvp(command[0], command)

        child_pid = pid
        child_fd = fd
        sync_winsize()
        signal.signal(signal.SIGWINCH, sync_winsize)

        while True:
            ready, _, _ = select.select([fd, sys.stdin.fileno()], [], [], 0.2)

            if fd in ready:
                try:
                    data = os.read(fd, 1024)
                except OSError:
                    break

                if not data:
                    break

                os.write(sys.stdout.fileno(), data)
                buffer = (buffer + data)[-BUFFER_SIZE:]

                clean = re.sub(rb"\x1b\[[0-?]*[ -/]*[@-~]", b"", buffer).decode(
                    errors="ignore"
                )

                if "You've hit your session limit" in clean:
                    reset_match = RESET_PATTERN.search(clean)

                    if reset_match:
                        reset = reset_match.group(1) + reset_match.group(2)
                        print(f"\nSession limit reached. Reset: {reset}")

                    os.kill(pid, signal.SIGTERM)

                    return 1, clean

            if sys.stdin.fileno() in ready:
                data = os.read(sys.stdin.fileno(), 1024)

                if not data:
                    break

                if b"\x03" in data:  # Ctrl-C
                    os.kill(pid, signal.SIGTERM)
                    break

                os.write(fd, data)

    finally:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_settings)

    if child_pid:
        try:
            os.waitpid(child_pid, 0)
        except ChildProcessError:
            pass

    child_fd = None

    return 1, buffer.decode(errors="ignore")


def wait_until(reset):
    # Deliberately naive/local: `reset` is a wall-clock time parsed from
    # Claude CLI's own message (shown in the user's local time), so `now`
    # must be local too for the comparison below to mean anything.
    now = datetime.now()  # noqa: DTZ005

    target = datetime.strptime(reset.upper(), "%I:%M%p").replace(  # noqa: DTZ007
        year=now.year, month=now.month, day=now.day
    )

    if target <= now:
        target += timedelta(days=1)

    seconds = int((target - now).total_seconds()) + 10

    print(f"\nWaiting {seconds}s until {target}")
    time.sleep(seconds)


def main():
    signal.signal(signal.SIGINT, forward_signal)
    signal.signal(signal.SIGTERM, forward_signal)

    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", help="Claude session id to resume")

    args = parser.parse_args()

    if args.resume:
        command = ["claude", "--resume", args.resume]
    else:
        command = ["claude"]

    while True:
        code, output = run_claude(command)
        clean = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", output)

        if code == 0:
            return 0

        match = RESET_PATTERN.search(clean)

        if not match:
            return code

        reset = match.group(1) + match.group(2)

        print(f"\nSession limit reached. Reset: {reset}")

        wait_until(reset)

        print("\nResuming Claude...")
        resume = RESUME_PATTERN.search(clean)

        if resume:
            session_id = resume.group(1)
            command = ["claude", "--resume", session_id]
        else:
            command = ["claude", "--continue"]


if __name__ == "__main__":
    raise SystemExit(main())
