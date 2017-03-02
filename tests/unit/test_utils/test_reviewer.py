import datetime
import importlib
import unittest

from note.utils import date
from note.utils.review_algorithm import Grade, ReviewAlgorithm, ReviewInfo


class TestReviewAlgorithm(unittest.TestCase):
    def setUp(self):
        self.review_algorithm = ReviewAlgorithm()

    def test_promptly_review_1(self):
        review_infos = [
            [10, 1.7, 10],
            [10, 1.7, 9],
            [10, 1.7, 11],
        ]
        grades = [
            Grade.EASY,
            Grade.EASY,
            Grade.EASY,
        ]
        targets = [
            [18, 1.8, 18],
            [17, 1.8, 17],
            [20, 1.8, 20],
        ]
        self._check(review_infos, grades, targets)

    def test_promptly_review_2(self):
        review_infos = [
            [10, 1.7, 10],
            [10, 1.7, 9],
            [10, 1.7, 11],
        ]
        grades = [
            Grade.REMEMBERED,
            Grade.REMEMBERED,
            Grade.REMEMBERED,
        ]
        targets = [
            [17, 1.7, 17],
            [16, 1.7, 16],
            [19, 1.7, 19],
        ]
        self._check(review_infos, grades, targets)

    def test_promptly_review_3(self):
        review_infos = [
            [10, 1.7, 10],
            [10, 1.7, 9],
            [10, 1.7, 11],
        ]
        grades = [
            Grade.FORGOTTEN,
            Grade.FORGOTTEN,
            Grade.FORGOTTEN,
        ]
        targets = [
            [13, 1.3, 1],
            [12, 1.3, 1],
            [15, 1.3, 1]
        ]
        self._check(review_infos, grades, targets)

    def test_early_review_1(self):
        review_infos = [
            [10, 1.7, 6],
        ]
        grades = [
            Grade.EASY,
        ]
        targets = [
            [15, 1.7, 15],
        ]
        self._check(review_infos, grades, targets)

    def test_early_review_2(self):
        review_infos = [
            [10, 1.7, 6],
            [12, 2, 8],
            [12, 2, 1],
        ]
        grades = [
            Grade.REMEMBERED,
            Grade.REMEMBERED,
            Grade.REMEMBERED,
        ]
        targets = [
            [8, 1.3, 8],
            [11, 8 / 6, 11],
            [2, 1.3, 2]
        ]
        self._check(review_infos, grades, targets)

    def test_early_review_3(self):
        review_infos = [
            [10, 1.7, 6],
            [12, 2, 8],
        ]
        grades = [
            Grade.FORGOTTEN,
            Grade.FORGOTTEN,
        ]

        targets = [
            [8, 1.3, 1],
            [11, 1.3, 1],
        ]
        self._check(review_infos, grades, targets)

    def test_late_review_1(self):
        review_infos = [
            [10, 1.7, 15],
        ]
        grades = [
            Grade.EASY,
        ]

        targets = [
            [27, 1.8, 27],
        ]
        self._check(review_infos, grades, targets)

    def test_late_review_2(self):
        review_infos = [
            [10, 1.7, 15],
            [6, 2, 44]
        ]
        grades = [
            Grade.REMEMBERED,
            Grade.REMEMBERED
        ]
        targets = [
            [26, 1.7, 26],
            [88, 2, 88]
        ]
        self._check(review_infos, grades, targets)

    def test_late_review_3(self):
        review_infos = [
            [10, 1.7, 15],
            [9, 2, 44]
        ]
        grades = [
            Grade.FORGOTTEN,
            Grade.FORGOTTEN
        ]
        targets = [
            [7, 1.7, 1],
            [2, 2, 1],
        ]
        self._check(review_infos, grades, targets)

    @staticmethod
    def today(lt, days):
        def warp():
            return lt + datetime.timedelta(days=days)

        return warp

    def _check(self, review_infos, grades, targets):
        for review_info, grade, target in zip(review_infos, grades, targets):
            # days表示实际在几天之后来复习的
            fd, ef, days = review_info
            lt = datetime.date(2016, 2, 1)
            nt = date.add(lt, fd)
            review_info = fd, ef, lt, nt

            # mock今天
            date.today = self.today(lt, days)

            fd, ef, days = target
            lt = date.today()

            nt = date.add(lt, days)
            target = fd, ef, lt, nt

            review_info = ReviewInfo(*review_info)
            target = ReviewInfo(*target)
            result = self.review_algorithm.review(review_info, grade)

            self.assertEqual(result, target)

    @classmethod
    def tearDownClass(cls):
        importlib.reload(date)
