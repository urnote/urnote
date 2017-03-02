"""
集成测试
"""
import filecmp
import shutil
import unittest
from unittest.mock import call

from integration.base_test_case import CommandTestCase, WorkspaceTestCase
from integration.config import (
    VIR_ROOT_DIR, ExpectedDbPath, ExpectedRootDir, VIR_DB_PATH)
from integration.tools import DBTools
from note.infrastructure.error import CMDError
from note.module.element import RunResult


class HelpTest(CommandTestCase):
    """测试note --help正确工作"""

    def test(self):
        with self.assertRaises(SystemExit):
            self.run_app('--help')
        expected = [
            call.show_prompt("{}".format(self.controller.parser.format_help()))]
        self.assertEqual(self.mock_view.method_calls, expected)


class InitTest(WorkspaceTestCase):
    """测试note init正确工作

    正常情况下将在当前目录下创建仓库,由于使用当前目录下建立仓库
    可能造成文件混乱,因此需要指定根目录
    """

    def test(self):
        self.run_app('init')

        expected = []
        self.assertEqual(self.mock_view.method_calls, expected)

    def test_multi_init(self):
        self.run_app('init')
        self.run_app('init')

        expected = [call.show_error(exc=CMDError(CMDError.INIT_CMD_ERROR, ))]
        self.assertEqual(self.mock_view.method_calls, expected)


class StatusTest(WorkspaceTestCase):
    """测试note status正确工作
    """

    def test(self):
        self.run_app('status')

        expected = [call.show_error(exc=CMDError(CMDError.UNINITIALIZED))]
        self.assertEqual(self.mock_view.method_calls, expected)

    def test_empty_workspace(self):
        self.run_app('init')
        self.run_app('status')

        expected = [call.show_run_result(RunResult())]
        self.assertEqual(self.mock_view.method_calls, expected)

    def test_case1_status(self):
        shutil.rmtree(VIR_ROOT_DIR)
        shutil.copytree(ExpectedRootDir('case1', 'pre'), VIR_ROOT_DIR)

        self.run_app('status')

        self.assertTrue(self.mock_view.show_run_result.called)

        d = filecmp.dircmp(VIR_ROOT_DIR,
                           ExpectedRootDir('case1', 'after_status'),
                           ['note.db3'])
        self.assertFalse(d.diff_files)
        equal = DBTools.cmp_db(VIR_DB_PATH,
                               ExpectedDbPath('case1', 'after_status'))
        self.assertTrue(equal)

    def test_case1_commit(self):
        shutil.rmtree(VIR_ROOT_DIR)
        shutil.copytree(ExpectedRootDir('case1', 'pre'), VIR_ROOT_DIR)

        self.run_app('commit')

        # 测试控制台的输出
        expected = []
        self.assertEqual(self.mock_view.method_calls, expected)

        # 测试处理后的文件内容符合预期
        d = filecmp.dircmp(VIR_ROOT_DIR,
                           ExpectedRootDir('case1', 'after_commit'),
                           ['note.db3'])
        self.assertFalse(d.diff_files)
        equal = DBTools.cmp_db(VIR_DB_PATH,
                               ExpectedDbPath('case1', 'after_commit'))
        self.assertTrue(equal)


if __name__ == '__main__':
    unittest.main()
