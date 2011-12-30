#!/usr/bin/env python
# coding=utf-8
from datetime import datetime, timedelta
from timestring import interval_string
import unittest


class TimeStringTestCase(unittest.TestCase):
    """Unit tests for the timestring module."""

    def setUp(self):
        self.start = datetime(2011, 1, 1)

    def test_same(self):
        self.assertEqual(interval_string(self.start, self.start), "0 seconds")

    def test_sub_second(self):
        end = self.start + timedelta(milliseconds=200)
        self.assertEqual(interval_string(self.start, end), "0 seconds")

    def test_seconds(self):
        end = self.start + timedelta(seconds=1)
        self.assertEqual(interval_string(self.start, end), "1 second")

    def test_seconds_plural(self):
        end = self.start + timedelta(seconds=2)
        self.assertEqual(interval_string(self.start, end), "2 seconds")

    def test_minutes(self):
        end = self.start + timedelta(minutes=1)
        self.assertEqual(interval_string(self.start, end), "1 minute")

    def test_minutes_plural(self):
        end = self.start + timedelta(minutes=2)
        self.assertEqual(interval_string(self.start, end), "2 minutes")

    def test_hours(self):
        end = self.start + timedelta(hours=1)
        self.assertEqual(interval_string(self.start, end), "1 hour")

    def test_hours_plural(self):
        end = self.start + timedelta(hours=2)
        self.assertEqual(interval_string(self.start, end), "2 hours")

    def test_days(self):
        end = self.start + timedelta(days=1)
        self.assertEqual(interval_string(self.start, end), "1 day")

    def test_days_plural(self):
        end = self.start + timedelta(days=2)
        self.assertEqual(interval_string(self.start, end), "2 days")

    def test_weeks(self):
        end = self.start + timedelta(weeks=1)
        self.assertEqual(interval_string(self.start, end), "1 week")

    def test_weeks_plural(self):
        end = self.start + timedelta(weeks=2)
        self.assertEqual(interval_string(self.start, end), "2 weeks")

    def test_months(self):
        # 1 month from self.start.
        end = datetime(2011, 2, 1)
        self.assertEqual(interval_string(self.start, end), "1 month")

    def test_months_plural(self):
        # 2 months from self.start.
        end = datetime(2011, 3, 1)
        self.assertEqual(interval_string(self.start, end), "2 months")

    def test_years(self):
        # 1 year from self.start.
        end = datetime(2012, 1, 1)
        self.assertEqual(interval_string(self.start, end), "1 year")

    def test_years_plural(self):
        # 2 years from self.start.
        end = datetime(2013, 1, 1)
        self.assertEqual(interval_string(self.start, end), "2 years")

    def test_years_leap_year_short(self):
        # 2012 is a leap year.
        start = datetime(2012, 2, 29)
        end = datetime(2013, 2, 28)
        self.assertEqual(interval_string(start, end), "11 months")

    def test_years_leap_year(self):
        # 2012 is a leap year.
        start = datetime(2012, 2, 29)
        end = datetime(2013, 3, 1)
        self.assertEqual(interval_string(start, end), "1 year")


if __name__ == "__main__":
    unittest.main()
