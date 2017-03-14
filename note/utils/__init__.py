import operator
import os as os_
import string
import sys
import time
from contextlib import contextmanager

from . import date

__all__ = ['Base', 'timeit', 'suppress_stdout', 'truncate',
           'truncate_for_display']


class Base:
    """
    参考：
        http://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes
        http://stackoverflow.com/questions/4522617/equality-of-python-classes-using-slots?noredirect=1&lq=1
    """

    def __eq__(self, other):
        """
        比较的时候：
            两个对象都是普通对象，且类型相同
            两个对象都是有slot的对象，类型相同
            两个对象都有slot和__dict__,类型相同

        对于slot的比较，之比较self本身的__slot__中存在的属性，不比较继承的部分
            参考:http://stackoverflow.com/questions/472000/usage-of-slots
        """
        if isinstance(other, self.__class__):
            slot_equal = True
            if hasattr(self, "__slots__"):
                attr_getters = [operator.attrgetter(attr) for attr in
                                self.__slots__]
                slot_equal = all(
                    getter(self) == getter(other) for getter in attr_getters)
            dict_equal = self.__dict__ == other.__dict__
            return slot_equal and dict_equal
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        """如果要实现集合，字典键等地方的相等性判断需要实现该方法"""

    def __repr__(self):
        attr_value_map = {}
        if hasattr(self, "__slots__"):
            for attr in self.__slots__:
                attr_value_map[attr] = getattr(self, attr)
        for key, value in self.__dict__.items():
            attr_value_map[key] = value
        return str(attr_value_map)

    __str__ = __repr__


def timeit(func):
    def count(*args, **kwargs):
        start = time.time()
        try:
            res = func(*args, **kwargs)
        except SystemExit:
            res = None
            print('Exit')
        finally:
            time_ = time.time() - start
            count.time = '{:f} ms'.format(1000 * time_)
        return res

    return count


@contextmanager
def suppress_stdout():
    stdout = None
    try:
        stdout, sys.stdout = sys.stdout, open(os_.devnull, 'w')
        yield
    finally:
        sys.stdout = stdout


def truncate(msg, width=80, keep_newline=False):
    """
    将字符串截取为80长度,如果超过80,末尾以...表示,
    keep_newline:截取过程中会保留最后的\n.如果传递进来的是bytes,则会保留最后的b'\n'
    """
    assert isinstance(msg, (str, bytes))
    assert width >= 3

    if isinstance(msg, str):
        endswith_newline = False
        if keep_newline and msg[-1] == '\n':
            endswith_newline = True
            msg = msg[:-1]
        if len(msg) > width:
            msg = msg[:width - 3] + '...'
        return msg + ('\n' if endswith_newline else '')
    elif isinstance(msg, bytes):
        endswith_newline = False
        if keep_newline and msg[-1] == b'\n':
            endswith_newline = True
            msg = msg[:-1]
        if len(msg) > width:
            msg = msg[:width - 3] + b'...'
        return msg + (b'\n' if endswith_newline else b'')
    else:
        raise RuntimeError


def truncate_for_display(msg, width=80, keep_newline=False):
    """
    将msg截断用于控制台显示,使显示的宽度不超过width,超出的部分用...表示
    keep_newline将保留最后一个\n

    原理如下:
        如果是Ascii范围的字符,不可显示的宽度为0,可显示的宽度为1.
        如果不是Ascii范围的字符,都认为宽度是2(有些字符显示宽度可能并不等于2,
        但是中文宽度都是2).
    """
    assert isinstance(msg, str), 'msg 必须是Unicode字符串'
    assert width >= 3
    printable_chars = set(string.printable)

    endswith_newline = False
    if keep_newline and msg[-1] == '\n':
        msg = msg[:-1]
        endswith_newline = True

    # 记录[(长度,坐标),(长度,坐标)...],其实最多记录最后的3个元素就可以了
    records = []
    length = 0
    for i, char in enumerate(msg):
        if ord(char) < 128:
            if char in printable_chars:
                length += 1
                records.append((length, i + 1))
        else:
            length += 2
            records.append((length, i + 1))
        if length > width:
            for l, c in reversed(records):
                if l < width - 2:
                    msg = msg[:c] + '...'
                    break
            break
    return msg + ('\n' if endswith_newline else '')
