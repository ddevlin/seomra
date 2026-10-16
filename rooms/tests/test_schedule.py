from datetime import date

from django.test import SimpleTestCase

from rooms.schedule import parse_date_param, week_days, week_start


class WeekHelpersTests(SimpleTestCase):
    def test_week_start_is_monday(self):
        self.assertEqual(week_start(date(2030, 1, 9)), date(2030, 1, 7))  # Wednesday -> Monday
        self.assertEqual(week_start(date(2030, 1, 7)), date(2030, 1, 7))  # Monday stays
        self.assertEqual(week_start(date(2030, 1, 6)), date(2029, 12, 31))  # Sunday -> previous Monday

    def test_week_days_returns_seven_consecutive_days(self):
        days = week_days(date(2030, 1, 7))
        self.assertEqual(len(days), 7)
        self.assertEqual(days[0], date(2030, 1, 7))
        self.assertEqual(days[-1], date(2030, 1, 13))


class ParseDateParamTests(SimpleTestCase):
    def test_valid_iso_date(self):
        self.assertEqual(parse_date_param("2030-01-07", date(2000, 1, 1)), date(2030, 1, 7))

    def test_garbage_falls_back(self):
        fallback = date(2000, 1, 1)
        for value in [None, "", "banana", "2026-13-45", "07/01/2030"]:
            with self.subTest(value=value):
                self.assertEqual(parse_date_param(value, fallback), fallback)
