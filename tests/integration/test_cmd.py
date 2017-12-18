"""
集成测试
"""
import unittest
from unittest.mock import call

from integration.base_test_case import (EmptyWorkspaceTestCase,
                                        WorkspaceTestCases)
from note.infrastructure.error import CMDError
from note.module.visitor import ReportAfterStatus


class HelpTest(EmptyWorkspaceTestCase):
    """测试note --help正确工作"""

    def test(self):
        with self.assertRaises(SystemExit):
            self.run_app('--help')

        # check
        expected = [
            call.show("{}".format(self.controller.parser.format_help()))
        ]
        self.assertEqual(self.mock_view.method_calls, expected)


class InitTest(EmptyWorkspaceTestCase):
    """测试note init正确工作"""

    def test(self):
        self.run_app('init')

        # check
        expected = []
        self.assertEqual(self.mock_view.method_calls, expected)

    def test_multi_init(self):
        self.run_app('init')
        self.run_app('init')

        # check
        expected = [call.show_error(exc=CMDError(CMDError.INIT_CMD_ERROR,
                                                 root_dir=self.TEMP_PATH))]
        self.assertEqual(self.mock_view.method_calls, expected)


class EmptyWorkspaceStatusTest(EmptyWorkspaceTestCase):
    def test(self):
        self.run_app('status')

        # check
        expected = [call.show_error(exc=CMDError(CMDError.UNINITIALIZED))]
        self.assertEqual(self.mock_view.method_calls, expected)

    def test_empty_workspace(self):
        self.run_app('init')
        self.run_app('status')

        # check
        expected = [call.show_report_after_status(ReportAfterStatus())]
        self.assertEqual(self.mock_view.method_calls, expected)


class Case1Test(WorkspaceTestCases.WorkspaceTestCase):
    """一些最基本的测试
    测试了９种笔记状态的转变"""
    CASE_NAME = 'case1'

    def _check_status(self):
        self.assertTrue(self.mock_view.show_report_after_status.called)

    def _check_commit(self):
        self.assertEqual(self.mock_view.show_report_after_commit.call_count, 1)


class Case2Test(WorkspaceTestCases.WorkspaceTestCase):
    """打乱了case1中的一些顺序后的测试"""
    CASE_NAME = 'case2'

    def _check_status(self):
        self.assertTrue(self.mock_view.show_report_after_status.called)

    def _check_commit(self):
        self.assertEqual(self.mock_view.show_report_after_commit.call_count, 1)


class Case3Test(WorkspaceTestCases.WorkspaceTestCase):
    """基于case1的测试用例，在内容中随机加入了answer结尾标志符
    测试了可以程序正确的处理＂---＂分隔符"""
    CASE_NAME = 'case3'

    def _check_status(self):
        self.assertTrue(self.mock_view.show_report_after_status.called)

    def _check_commit(self):
        self.assertEqual(self.mock_view.show_report_after_commit.call_count, 1)


class Case4Test(WorkspaceTestCases.WorkspaceTestCase):
    """测试可以使用非快捷方式"""
    CASE_NAME = 'case4'

    def _args(self):
        return ['-nl']

    def _check_status(self):
        self.assertTrue(self.mock_view.show_report_after_status.called)

    def _check_commit(self):
        self.assertEqual(self.mock_view.show_report_after_commit.call_count, 1)


class Case5Test(WorkspaceTestCases.WorkspaceTestCase):
    """测试可以使用非快捷方式,且正确处理---分割答案"""
    CASE_NAME = 'case5'

    def _args(self):
        return ['-nl']

    def _check_status(self):
        self.assertTrue(self.mock_view.show_report_after_status.called)

    def _check_commit(self):
        self.assertEqual(self.mock_view.show_report_after_commit.call_count, 1)


class Case6Test(WorkspaceTestCases.WorkspaceTestCase):
    """测试单文件复习"""
    CASE_NAME = 'case6'

    def _args(self):
        return ['-s']

    def _check_status(self):
        self.assertTrue(self.mock_view.show_report_after_status.called)

    def _check_commit(self):
        self.assertEqual(self.mock_view.show_report_after_commit.call_count, 1)


if __name__ == '__main__':
    unittest.main()
