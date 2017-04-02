import unittest
from unittest.mock import patch, call

from note.infrastructure.error import UserError
from note.module.visitor import (ReportAfterStatus, LocatedQuestions,
                                 ReportAfterCommit)
from note.view import View


class TestHandleResultView(unittest.TestCase):
    def setUp(self):
        with patch('note.view.StdoutHelper'):
            self.view = View()
            self.stdouthelper = self.view.stdouthelper

    def test_show(self):
        msg = 'foo'
        self.view.show(msg)

        # check
        expected = [call.print('\nfoo\n')]
        self.stdouthelper.assert_has_calls(expected)

    def test_show_error1(self):
        msg = 'error'
        self.view.show_error(msg=msg)

        # check
        expected = [call.print_red('\nerror\n')]
        self.stdouthelper.assert_has_calls(expected)

    def test_show_error2(self):
        error = UserError()
        msg = 'bar'

        # check
        with self.assertRaises(AssertionError) as err:
            self.view.show_error(error, msg=msg)
        self.assertEqual(str(err.exception), '不能同时传递2个参数')

    @patch('note.view.UserError')
    def test_show_error3(self, error_class):
        error = error_class()
        error.message = ['foo', 'bar']

        self.view.show_error(error)

        # check
        expected = [call.print_red('\nfoo\nbar\n')]
        self.stdouthelper.assert_has_calls(expected)

    def test_show_report_after_status(self):
        new_question = LocatedQuestions('new', ['new1', 'new2'])
        reviewed_question = LocatedQuestions('reviewed',
                                             ['reviewed1', 'reviewed2'])
        paused_question = LocatedQuestions('paused', ['paused1', 'paused2'])
        report = ReportAfterStatus()
        report.new_qs_report = [new_question]
        report.reviewed_qs_report = [reviewed_question]
        report.paused_qs_report = [paused_question]
        report.need_reviewed_num = 2

        self.view.show_report_after_status(report)

        # check
        expected1 = [
            call.print_blue('\n新增了 2 个问题:\n'),
            call.print_green('    new:\n'),
            call.print_yellow('        new1\n'),
            call.print_yellow('        new2\n'),
        ]
        expected2 = [
            call.print_blue('\n复习了 2 个问题:\n'),
            call.print_green('    reviewed:\n'),
            call.print_yellow('        reviewed1\n'),
            call.print_yellow('        reviewed2\n'),
        ]
        expected3 = [
            call.print_blue('\n暂停了 2 个问题:\n'),
            call.print_green('    paused:\n'),
            call.print_yellow('        paused1\n'),
            call.print_yellow('        paused2\n'),
        ]
        expected4 = [
            call.print_blue('\n2 个问题需要复习\n'),
        ]
        expected = expected1 + expected2 + expected3 + expected4
        self.stdouthelper.assert_has_calls(expected)

    def test_show_report_after_commit_1(self):
        report = ReportAfterCommit()
        report.new_num = 1
        report.reviewed_num = 2
        report.paused_num = 3
        report.need_reviewed_num = 4

        self.view.show_report_after_commit(report)

        # check
        expected = [
            call.print('\n'),
            call.print_blue('新增了 1 个问题\n'),
            call.print_blue('复习了 2 个问题\n'),
            call.print_blue('暂停了 3 个问题\n'),
            call.print_blue('\n4 个问题需要复习\n'),
        ]
        self.stdouthelper.assert_has_calls(expected)

    def test_show_report_after_commit_2(self):
        report = ReportAfterCommit()
        report.new_num = 0
        report.reviewed_num = 0
        report.paused_num = 0
        report.need_reviewed_num = 4

        self.view.show_report_after_commit(report)

        # check
        expected = [
            call.print_blue('\n4 个问题需要复习\n'),
        ]
        self.stdouthelper.assert_has_calls(expected)

    def test_show_report_after_commit_3(self):
        report = ReportAfterCommit()
        report.new_num = 1
        report.reviewed_num = 2
        report.paused_num = 3
        report.need_reviewed_num = 0

        self.view.show_report_after_commit(report)

        # check
        expected = [
            call.print('\n'),
            call.print_blue('新增了 1 个问题\n'),
            call.print_blue('复习了 2 个问题\n'),
            call.print_blue('暂停了 3 个问题\n'),
        ]
        self.stdouthelper.assert_has_calls(expected)


if __name__ == '__main__':
    unittest.main()
