import datetime
import unittest

from note.utils.date import *


class TestDate(unittest.TestCase):
    def test_to_date(self):
        date = '2016-05-26'
        date2 = datetime.date(2016, 5, 26)
        self.assertEqual(to_date(date), date2)

    def test_to_date_stamp(self):
        date = '2016-05-26'
        date2 = datetime.date(2016, 5, 26)
        self.assertEqual(date, to_stamp(date2))

    def test_add(self):
        values = {
            ('2016-06-26', 4): datetime.date(2016, 6, 30),
            (datetime.date(2016, 6, 26), 6): datetime.date(2016, 7, 2),
            (datetime.date(2016, 6, 26), 6, 'str'): '2016-07-02'
        }

        for arg, result in values.items():
            res = add(*arg)
            self.assertEqual(res, result)
