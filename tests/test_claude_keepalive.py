import importlib.util
import os
import unittest
from datetime import datetime
from unittest import mock

MODULE_PATH = os.path.join(os.path.dirname(__file__), "..", "claude-keepalive.py")
spec = importlib.util.spec_from_file_location("claude_keepalive", MODULE_PATH)
ck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ck)


class ResetPatternTests(unittest.TestCase):
    def test_matches_am_time(self):
        m = ck.RESET_PATTERN.search("You've hit your session limit, resets 3:45am tomorrow")
        self.assertEqual(m.group(1) + m.group(2), "3:45am")

    def test_matches_pm_time(self):
        m = ck.RESET_PATTERN.search("resets 11:59pm")
        self.assertEqual(m.group(1) + m.group(2), "11:59pm")

    def test_no_match(self):
        self.assertIsNone(ck.RESET_PATTERN.search("no reset info here"))


class ResumePatternTests(unittest.TestCase):
    def test_extracts_session_id(self):
        m = ck.RESUME_PATTERN.search(
            "Run claude --resume ab12cd34-e5f6-7890-abcd-ef1234567890 to continue"
        )
        self.assertEqual(m.group(1), "ab12cd34-e5f6-7890-abcd-ef1234567890")

    def test_no_match(self):
        self.assertIsNone(ck.RESUME_PATTERN.search("nothing to resume here"))


class WaitUntilTests(unittest.TestCase):
    @mock.patch.object(ck, "time")
    @mock.patch.object(ck, "datetime")
    def test_waits_until_later_today(self, mock_datetime, mock_time):
        mock_datetime.now.return_value = datetime(2026, 7, 28, 10, 0, 0)
        mock_datetime.strptime.side_effect = datetime.strptime

        ck.wait_until("10:05am")

        mock_time.sleep.assert_called_once_with(5 * 60 + 10)

    @mock.patch.object(ck, "time")
    @mock.patch.object(ck, "datetime")
    def test_rolls_to_next_day_if_time_already_passed(self, mock_datetime, mock_time):
        mock_datetime.now.return_value = datetime(2026, 7, 28, 10, 0, 0)
        mock_datetime.strptime.side_effect = datetime.strptime

        ck.wait_until("9:00am")

        mock_time.sleep.assert_called_once_with(23 * 3600 + 10)


if __name__ == "__main__":
    unittest.main()
