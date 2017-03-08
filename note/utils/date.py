"""
该模块提供了用于处理日期的操作:
    1. 日期加减法
    2. 日期的表现形式转化
"""

import datetime

__all__ = ['ChinaTz', 'to_date', 'to_stamp', 'add', 'today']


class ChinaTz(datetime.tzinfo):
    """实现北京时间的类"""

    def utcoffset(self, dt):
        return datetime.timedelta(hours=8)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return 'UTC+8'


def to_date(date):
    """转变为日期对象

    Args:
        date: 日期.可以是字符串,可以是date对象

    Returns:
        返回date对象
    """
    assert isinstance(date, (str, datetime.date))

    if isinstance(date, str):
        try:
            year, month, day = map(int, date.split("-"))
            date = datetime.date(year, month, day)
        except:
            raise ValueError
    if isinstance(date, datetime.datetime):
        return date.date()
    return date


def to_stamp(date):
    """转变为date时间戳

    Args:
        date: 日期.可以是字符串,可以是date对象

    Returns:
        返回date的时间戳,以-连接
    """
    assert isinstance(date, (str, datetime.date))

    if isinstance(date, datetime.date):
        return date.strftime("%Y-%m-%d")
    return date


def today():
    return datetime.date.today()


def add(first, second, return_type='date'):
    """处理日期加法

    支持日期加数字,日期可以是字符串也可以是date类型

    Returns:
        date类型
    """
    assert isinstance(first, (str, datetime.date))
    assert isinstance(second, int)

    first = to_date(first)
    date = first + datetime.timedelta(days=second)
    if return_type == 'date':
        return date
    elif return_type == 'str':
        return to_stamp(date)
    else:
        raise ValueError
