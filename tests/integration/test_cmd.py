"""
集成测试
"""
import unittest
from unittest.mock import call

from integration.base_test_case import (EmptyWorkspaceTestCase,
                                        WorkspaceTestCases)
from note.infrastructure.error import CMDError
from note.module.element import RunResult


class HelpTest(EmptyWorkspaceTestCase):
    """测试note --help正确工作"""

    def test(self):
        with self.assertRaises(SystemExit):
            self.run_app('--help')

        # check
        expected = [
            call.show_prompt("{}".format(self.controller.parser.format_help()))
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
        expected = [call.show_run_result(RunResult())]
        self.assertEqual(self.mock_view.method_calls, expected)


class Case1Test(WorkspaceTestCases.WorkspaceTestCase):
    CASE_NAME = 'case1'

    def _check_status(self):
        self.assertTrue(self.mock_view.show_run_result.called)

    def _check_commit(self):
        self.assertEqual(self.mock_view.method_calls, [])


if __name__ == '__main__':
    unittest.main()
