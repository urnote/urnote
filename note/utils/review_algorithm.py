import datetime
import math
from enum import Enum

from note.utils import Base, date

__all__ = ['ReviewAlgorithm', 'Grade', 'ReviewInfo']


class Grade(Enum):
    EASY = 1
    REMEMBERED = 2
    FORGOTTEN = 3


class AlgorithmConfig:
    DRILL_INTERVAL = 10

    GRADE_EF_MAP = {
        Grade.EASY: 0.1,
        Grade.REMEMBERED: 0,
        Grade.FORGOTTEN: -0.3
    }

    EXPAND_FACTOR = 0.1

    INTERVAL_OF_NEW_ITEM = 3

    INIT_EF = 1.7


class ReviewInfo(Base):
    __slots__ = ('fd', 'ef', 'lt', 'nt')

    def __init__(self, fd=None, ef=None, lt=None, nt=None):
        self.fd = fd
        self.ef = ef
        self.lt = lt
        self.nt = nt

    def __iter__(self):
        for item in (self.fd, self.ef, self.lt, self.nt):
            yield item


class ReviewAlgorithm:
    algorithm_config = AlgorithmConfig

    def new(self, interval=None, date_offset=None):
        """生成新加入学习计划的item的复习信息"""
        if interval is None:
            fd = self.algorithm_config.INTERVAL_OF_NEW_ITEM
        else:
            fd = int(interval)

        ef = self.algorithm_config.INIT_EF
        lt = self._calc_last_time(date_offset)
        nt = date.add(lt, fd)

        return ReviewInfo(fd, ef, lt, nt)

    @staticmethod
    def _calc_last_time(time):
        if time is None:
            lt = date.today()
        else:
            assert isinstance(time, int)
            lt = date.today() - datetime.timedelta(days=time)
        return lt

    def review(self, review_info: ReviewInfo, grade: Grade, date_offset=None):
        """处理复习了的item的复习信息"""
        fd, ef, lt, nt = (
            review_info.fd, review_info.ef, review_info.lt, review_info.nt)

        assert fd != 0

        today = date.today()
        actual_interval = (today - lt).days
        standard_interval = fd
        lt = self._calc_last_time(date_offset)

        if self._belong_to_promptly_review(standard_interval, actual_interval):
            return self._common_handle(ef, actual_interval, grade)
        elif self._belong_to_early_review(standard_interval, actual_interval):
            if grade == Grade.EASY:
                fd = math.ceil(actual_interval * ef) + (fd - actual_interval)

                # fd的最小值为1
                fd = int(fd) or 1
                nt = date.add(lt, fd)
                return ReviewInfo(fd, ef, lt, nt)
            elif grade == Grade.REMEMBERED or grade == Grade.FORGOTTEN:
                ef = self._calc_new_ef(fd, actual_interval, ef)
                return self._common_handle(ef, actual_interval, grade)
        elif self._belong_to_late_review(standard_interval, actual_interval):
            if grade == Grade.EASY or grade == Grade.REMEMBERED:
                return self._common_handle(ef, actual_interval, grade)
            elif grade == Grade.FORGOTTEN:
                fd = math.ceil(fd * fd / actual_interval)
                fd = int(fd) or 1
                nt = date.add(lt, 1)
                return ReviewInfo(fd, ef, lt, nt)

    def _belong_to_promptly_review(self, standard_interval,
                                   actual_interval: int):
        return (standard_interval * (1 - self.algorithm_config.EXPAND_FACTOR) <=
                actual_interval <=
                standard_interval * (1 + self.algorithm_config.EXPAND_FACTOR))

    def _belong_to_early_review(self, standard_interval, actual_interval):
        return (actual_interval <
                standard_interval * (1 - self.algorithm_config.EXPAND_FACTOR))

    def _belong_to_late_review(self, standard_interval, actual_interval):
        return (actual_interval >
                standard_interval * (1 + self.algorithm_config.EXPAND_FACTOR))

    def _calc_new_ef(self, fd, actual_interval, ef):
        last_fd = self._calc_last_fd(fd, ef)
        ef = actual_interval / last_fd
        ef = self._normalize_ef(ef)
        return ef

    @staticmethod
    def _calc_last_fd(fd, ef):
        value = fd // ef
        return value if value else 1

    def _common_handle(self, ef: float, actual_interval: int, grade: Grade):
        if grade == Grade.FORGOTTEN:
            return self._handle_forgotten_item(ef, actual_interval)
        elif grade in (Grade.EASY, Grade.REMEMBERED):
            return self._have_completed_review(ef, actual_interval, grade)
        else:
            raise ValueError('invalid grade:{}'.format(grade))

    def _handle_forgotten_item(self, ef, actual_interval):
        ef += (self.algorithm_config.GRADE_EF_MAP[Grade.FORGOTTEN] -
               self.algorithm_config.GRADE_EF_MAP[Grade.EASY])
        ef = self._normalize_ef(ef)

        fd = math.ceil(actual_interval * ef)
        fd = int(fd) or 1

        lt = date.today()
        nt = date.add(lt, 1)

        return ReviewInfo(fd, ef, lt, nt)

    def _have_completed_review(self, ef, actual_interval, grade):
        ef += self.algorithm_config.GRADE_EF_MAP[grade]
        ef = self._normalize_ef(ef)

        fd = math.ceil(actual_interval * ef)
        fd = int(fd) or 1

        lt = date.today()
        nt = date.add(date.today(), fd)

        return ReviewInfo(fd, ef, lt, nt)

    @staticmethod
    def _normalize_ef(ef):
        if ef < 1.3:
            ef = 1.3
        return ef

    @staticmethod
    def need_review(review_info: ReviewInfo):
        """判断该item是否需要复习"""
        return review_info.nt <= date.today()
