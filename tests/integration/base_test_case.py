import datetime
import gc
import importlib
import logging
import os
import shutil
import unittest
from unittest.mock import patch, Mock

from integration.config import VIR_ROOT_DIR
from kit import file_watcher
from kit.pattern import Singleton

from note.controller import Controller
from note.factory import (get_purger, get_parser, get_initializer,
                          get_runner, get_logger)
from note.view import RunResultView


class CommandTestCase(unittest.TestCase):
    """测试controller的行为正确"""

    def setUp(self):
        """初始化环境,保证每一组测试开始时,vir_env包含res中的文件"""
        self.mock_view = Mock(spec=RunResultView)

    def run_app(self, command):
        import sys
        sys.argv = ['note', command]
        view = self.mock_view
        self.controller = Controller(
            view, get_logger(), get_parser(view),
            get_purger=get_purger,
            get_runner=get_runner,
            get_initializer=get_initializer
        )
        self.controller.run()

    def tearDown(self):
        Singleton.clear()
        importlib.reload(logging)
        self.mock_view.reset_mock()
        del self.controller
        gc.collect()


class Enumeration(type):
    date = datetime.date

    def __instancecheck__(self, other):
        return isinstance(other, Enumeration.date)


class NewDate(datetime.date, metaclass=Enumeration):
    """
    http://stackoverflow.com/questions/4481954/python-trying-to-mock-datetime-date-today-but-not-working/25652721#25652721
    不使用mock,因为无法赋值,且可能无法正确执行isinstance检查
    """

    @classmethod
    def today(cls):
        return cls(2016, 11, 13)


class WorkspaceTestCase(CommandTestCase):
    """工作空间下行为测试

    会在当前目录下创建一个vir_env目录，结束后删除。重设程序当前工作空间为vir_env目录
    """

    def setUp(self):
        """初始化环境,保证每一组测试开始时,vir_env包含res中的文件"""
        super().setUp()
        self.patcher1 = patch('os.getcwd', return_value=VIR_ROOT_DIR)
        self.patcher1.start()

        datetime.date = NewDate
        assert datetime.date.today() == datetime.date(2016, 11, 13)

        file_watcher.watch()
        if os.path.exists(VIR_ROOT_DIR):
            shutil.rmtree(VIR_ROOT_DIR)
        os.mkdir(VIR_ROOT_DIR)

    def tearDown(self):
        file_watcher.close_all(echo=False)
        self.patcher1.stop()
        super().tearDown()

        # 删除的时候,由于logger还存在了对该文件的引用,所以会报
        # [WinError 32] 另一个程序正在使用此文件，进程无法访问

        # reload之后不再有logger对文件引用,但是下面3个类的对象引用了,
        # 目前不知道为什么,需要自己手动关闭:
        # {<class '_io.FileIO'>, <class '_io.TextIOWrapper'>,
        # <class '_io.BufferedWriter'>}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(VIR_ROOT_DIR)
