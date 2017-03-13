import datetime
import filecmp
import importlib
import logging
import os
import shutil
import unittest
from unittest.mock import patch, Mock

from integration.config import ExpectedRootDir, ExpectedDbPath
from integration.tools import DBTools
from note.controller import Controller
from note.objects import (get_purger, get_parser, get_initializer,
                          get_runner, get_logger, release,
                          get_status_result_visitor, get_commit_result_visitor)
from note.utils.os.fs import virtual_workspace
from note.utils.pattern import Singleton
from note.view import View


class CommandTestCase(unittest.TestCase):
    """测试controller的行为正确"""

    def setUp(self):
        """初始化环境,保证每一组测试开始时,vir_env包含res中的文件"""
        self.mock_view = Mock(spec=View)

    def tearDown(self):
        Singleton.clear()
        importlib.reload(logging)
        self.mock_view.reset_mock()

    def run_app(self, command):
        import sys
        sys.argv = ['note', command]
        view = self.mock_view
        self.controller = Controller(
            view, get_logger(), get_parser(view),
            get_purger=get_purger,
            get_runner=get_runner,
            get_initializer=get_initializer,
            get_status_result_visitor=get_status_result_visitor,
            get_commit_result_visitor=get_commit_result_visitor
        )
        self.controller.run()
        release()


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


class EmptyWorkspaceTestCase(CommandTestCase):
    TEMP_PATH = os.path.abspath('TEMPDIR')

    def setUp(self):
        """初始化环境,保证每一组测试开始时,vir_env包含res中的文件"""
        super().setUp()
        os.mkdir(self.TEMP_PATH)
        self.patcher = patch('os.getcwd', return_value=self.TEMP_PATH)
        self.patcher.start()

    def tearDown(self):
        shutil.rmtree(self.TEMP_PATH)
        self.patcher.stop()
        super().tearDown()


class WorkspaceTestCases:
    """
    嵌套的原因:http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class
    """

    class WorkspaceTestCase(CommandTestCase):
        """工作空间下行为测试

        会在当前目录下创建一个vir_env目录，结束后删除。重设程序当前工作空间为vir_env目录
        """

        CASE_NAME = None

        @classmethod
        def setUpClass(cls):
            cls.virtual_workspace = virtual_workspace(
                ExpectedRootDir(cls.CASE_NAME, 'pre')
            )

        def _compare_workspace(self, workspace):
            # 比较工作空间中的文件是否都一样
            d = filecmp.dircmp(self.root_path,
                               ExpectedRootDir(self.CASE_NAME, workspace),
                               ignore=['note.db3'])
            self.assertFalse(d.diff_files)
            equal = DBTools.cmp_db(self.db_path,
                                   ExpectedDbPath(self.CASE_NAME, workspace))
            self.assertTrue(equal)

        def test_status(self):
            self.run_app('status')

            # check
            self._check_status()
            self._compare_workspace('after_status')

        def _check_status(self):
            raise NotImplementedError

        def test_commit(self):
            self.run_app('commit')

            # check
            self._check_commit()
            self._compare_workspace('after_commit')

        def _check_commit(self):
            raise NotImplementedError

        def setUp(self):
            """初始化环境,保证每一组测试开始时,vir_env包含res中的文件"""
            super().setUp()
            self.root_path = self.virtual_workspace.enter()
            self.db_path = os.path.join(self.root_path, '.NOTE', 'note.db3')
            self.patcher = patch('os.getcwd', return_value=self.root_path)
            self.patcher.start()

            datetime.date = NewDate
            assert datetime.date.today() == datetime.date(2016, 11, 13)

        def tearDown(self):
            self.patcher.stop()
            self.virtual_workspace.exit()
            super().tearDown()
