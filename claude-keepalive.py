#!/usr/bin/env python3

import os
import pty
import tty
import select
import signal
import sys
import time
import re
import termios
import argparse
from datetime import datetime

BUFFER_SIZE = 4096
IGNORE_INITIAL_BYTES = 8192
RESET_PATTERN = re.compile(r"resets (\d+:\d+)(am|pm)")
RESUME_PATTERN = re.compile(r"claude --resume ([a-f0-9-]+)")

child_pid = None


def forward_signal(sig, frame):
    if child_pid:
        os.kill(child_pid, sig)


def run_claude(command):
    global child_pid

    buffer = b""
    seen = 0

    try:
        stdin_fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(stdin_fd)
        tty.setraw(stdin_fd)
        pid, fd = pty.fork()

        if pid == 0:
            os.execvp(command[0], command)

        child_pid = pid

        while True:
            ready, _, _ = select.select(
                [fd, sys.stdin.fileno()],
                [],
                [],
                0.2
            )

            if fd in ready:
                try:
                    data = os.read(fd, 1024)
                except OSError:
                    break

                if not data:
                    break

                os.write(sys.stdout.fileno(), data)
                seen += len(data)

                if seen > IGNORE_INITIAL_BYTES:
                    buffer = (buffer + data)[-BUFFER_SIZE:]

                clean = re.sub(
                    rb'\x1b\[[0-?]*[ -/]*[@-~]',
                    b'',
                    buffer
                ).decode(errors="ignore")
            
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
        termios.tcsetattr(
            stdin_fd,
            termios.TCSADRAIN,
            old_settings
        )

    if child_pid:
        try:
            os.waitpid(child_pid, 0)
        except ChildProcessError:
            pass

    return 1, buffer.decode(errors="ignore")


def wait_until(reset):
    now = datetime.now()

    target = datetime.strptime(
        reset.upper(),
        "%I:%M%p"
    ).replace(
        year=now.year,
        month=now.month,
        day=now.day
    )

    if target <= now:
        from datetime import timedelta
        target += timedelta(days=1)

    seconds = int((target - now).total_seconds()) + 10

    print(f"\nWaiting {seconds}s until {target}")
    time.sleep(seconds)


def main():
    signal.signal(signal.SIGINT, forward_signal)
    signal.signal(signal.SIGTERM, forward_signal)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--resume",
        help="Claude session id to resume"
    )

    args = parser.parse_args()

    signal.signal(signal.SIGINT, forward_signal)
    signal.signal(signal.SIGTERM, forward_signal)

    if args.resume:
        command = ["claude", "--resume", args.resume]
    else:
        command = ["claude"]

    while True:
        code, output = run_claude(command)
        clean = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', output)

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
