import importlib.util
import os
import pty
import re
import select
import sys
import time
import unittest
from datetime import datetime

MODULE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "claude-keepalive.py",
)


def load_module():
    spec = importlib.util.spec_from_file_location("claude_keepalive", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MOD = load_module()


class TestStripAnsi(unittest.TestCase):
    def test_strips_csi_sequences(self):
        raw = b"\x1b[31mYou've hit your session limit\x1b[0m \x1b[2K\x1b[1Aresets 3am"
        self.assertEqual(
            MOD.strip_ansi(raw), "You've hit your session limit resets 3am"
        )

    def test_strips_osc_sequences(self):
        raw = b"\x1b]0;claude\x07hello \x1b]8;;http://x\x1b\\world"
        self.assertEqual(MOD.strip_ansi(raw), "hello world")

    def test_normalizes_curly_apostrophe(self):
        raw = "You’ve hit your usage limit".encode()
        self.assertEqual(MOD.strip_ansi(raw), "You've hit your usage limit")


class TestFoundLimit(unittest.TestCase):
    def test_matches_known_phrases(self):
        for phrase in (
            "You've hit your session limit",
            "You've hit your usage limit",
            "You've reached your usage limit",
            "Claude usage limit reached",
            "5-hour limit reached",
        ):
            self.assertTrue(MOD.found_limit(f"blah {phrase} blah"), phrase)

    def test_is_case_insensitive(self):
        self.assertTrue(MOD.found_limit("YOU'VE HIT YOUR SESSION LIMIT"))

    def test_ignores_approaching_warning(self):
        self.assertFalse(MOD.found_limit("Approaching usage limit · resets 4pm"))

    def test_ignores_ordinary_output(self):
        self.assertFalse(MOD.found_limit("let's talk about rate limits in nginx"))


class TestParseReset(unittest.TestCase):
    def test_hour_only(self):
        self.assertEqual(MOD.parse_reset("limit · resets 3am"), "3:00am")

    def test_hour_and_minutes(self):
        self.assertEqual(MOD.parse_reset("resets 4:30pm"), "4:30pm")

    def test_will_reset_at_variant(self):
        self.assertEqual(MOD.parse_reset("Your limit will reset at 11:45pm"), "11:45pm")

    def test_resets_at_variant(self):
        self.assertEqual(MOD.parse_reset("resets at 12am"), "12:00am")

    def test_invalid_hour_rejected(self):
        self.assertIsNone(MOD.parse_reset("resets 99pm"))

    def test_no_match(self):
        self.assertIsNone(MOD.parse_reset("nothing to see here"))


class TestSecondsUntil(unittest.TestCase):
    def test_future_same_day(self):
        now = datetime(2026, 7, 20, 14, 0, 0)
        self.assertEqual(
            MOD.seconds_until("3:00pm", now), 3600 + MOD.RESET_MARGIN_SECONDS
        )

    def test_past_rolls_to_next_day(self):
        now = datetime(2026, 7, 20, 14, 0, 0)
        self.assertEqual(
            MOD.seconds_until("1:00pm", now),
            23 * 3600 + MOD.RESET_MARGIN_SECONDS,
        )

    def test_midnight(self):
        now = datetime(2026, 7, 20, 23, 0, 0)
        self.assertEqual(
            MOD.seconds_until("12:00am", now), 3600 + MOD.RESET_MARGIN_SECONDS
        )


class TestResumePattern(unittest.TestCase):
    def test_extracts_uuid(self):
        text = "Run claude --resume abcdef12-3456-7890-abcd-ef1234567890 to continue"
        match = MOD.RESUME_PATTERN.search(text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "abcdef12-3456-7890-abcd-ef1234567890")

    def test_rejects_partial_id(self):
        self.assertIsNone(MOD.RESUME_PATTERN.search("claude --resume abc123"))


class TestRunClaude(unittest.TestCase):
    """End-to-end: run_claude inside a real PTY against a fake claude."""

    def run_wrapped(self, fake_script):
        pid, fd = pty.fork()

        if pid == 0:  # PTY child: stdin/stdout are the slave side
            status = 1
            try:
                mod = load_module()
                code, limit_hit, clean = mod.run_claude(
                    [sys.executable, "-u", "-c", fake_script], ignore_initial=0
                )
                sys.stdout.write(f"\nRESULT code={code} limit={int(limit_hit)}\n")
                sys.stdout.flush()
                status = 0
            finally:
                os._exit(status)

        output = b""
        deadline = time.monotonic() + 30

        while time.monotonic() < deadline:
            ready, _, _ = select.select([fd], [], [], 0.5)
            if fd not in ready:
                continue
            try:
                chunk = os.read(fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            output += chunk

        _, status = os.waitpid(pid, 0)
        os.close(fd)
        self.assertEqual(os.waitstatus_to_exitcode(status), 0, output)

        match = re.search(rb"RESULT code=(\d+) limit=(\d)", output)
        self.assertIsNotNone(match, output)
        return int(match.group(1)), int(match.group(2)), output

    def test_normal_exit_passes_through_exit_code(self):
        code, limit, _ = self.run_wrapped(
            "import sys; sys.stdout.write('hi there\\n'); sys.exit(5)"
        )
        self.assertEqual(code, 5)
        self.assertEqual(limit, 0)

    def test_limit_banner_detected_and_child_stopped(self):
        code, limit, output = self.run_wrapped(
            "import sys, time\n"
            "sys.stdout.write('hello from claude\\n')\n"
            'sys.stdout.write("\\x1b[33mYou\'ve hit your usage limit\\x1b[0m")\n'
            "sys.stdout.write(' \\u2022 resets 2:30am\\n')\n"
            "time.sleep(30)\n"
        )
        self.assertEqual(limit, 1)
        self.assertIn(b"resets 2:30am", output)


if __name__ == "__main__":
    unittest.main()
