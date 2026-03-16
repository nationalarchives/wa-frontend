import unittest
from datetime import datetime, timezone

from app.lib.template_filters import humanise_date


class HumaniseDateTestCase(unittest.TestCase):
    def test_iso_string_with_z_suffix(self):
        self.assertEqual(humanise_date("2024-03-15T12:00:00Z"), "15 March '24")

    def test_iso_string_without_time(self):
        self.assertEqual(humanise_date("2024-03-15"), "15 March '24")

    def test_datetime_object(self):
        dt = datetime(2024, 3, 15, tzinfo=timezone.utc)
        self.assertEqual(humanise_date(dt), "15 March '24")

    def test_single_digit_day(self):
        self.assertEqual(humanise_date("2024-01-05"), "5 January '24")

    def test_invalid_value_returns_empty_string(self):
        self.assertEqual(humanise_date(12345), "")  # type: ignore[arg-type]
