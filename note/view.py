from note.infrastructure.error import UserError
from note.infrastructure.stdouthelper import StdoutHelper
from note.module.visitor import (ReportAfterStatus, LocatedQuestions,
                                 ReportAfterCommit)
from note.utils import truncate_for_display

LOCATION_MSG = '    {location}:\n'.format
QUESTION_MSG = '        {question}\n'.format


def _create_location_msg(location):
    msg = LOCATION_MSG(location=location)
    return truncate_for_display(msg, width=80, keep_newline=True)


def _create_question_msg(question):
    msg = QUESTION_MSG(question=question)
    return truncate_for_display(msg, width=80, keep_newline=True)


class View:
    def __init__(self):
        self.stdouthelper = StdoutHelper()

    def show(self, msg):
        self.stdouthelper.print_white('\n{}\n'.format(msg))

    def show_report_after_status(self, result: ReportAfterStatus):
        self._show_new_info(result)
        self._show_reviewed_info(result)
        self._show_paused_info(result)
        self._show_need_reviewed_info(result)

    def _show_new_info(self, result):
        self._show_report(result.new_qs_report, action='新增')

    def _show_reviewed_info(self, result):
        self._show_report(result.reviewed_qs_report, action='复习')

    def _show_paused_info(self, result):
        self._show_report(result.paused_qs_report, action='暂停')

    def _show_need_reviewed_info(self, result):
        if result.need_reviewed_num:
            self.stdouthelper.print_blue(
                '\n{} 个问题需要复习\n'.format(result.need_reviewed_num))

    def _show_report(self, report, action):
        """
        Args:
            report: 一个LocatedQuestions列表
            action:
        """
        assert action is not None

        if len(report):
            total = sum(
                len(located_questions.qs) for located_questions in report
            )
            self.stdouthelper.print_blue(
                '\n{}了 {} 个问题:\n'.format(action, total))

            for located_questions in report:
                assert isinstance(located_questions, LocatedQuestions)

                location_msg = _create_location_msg(
                    location=located_questions.location)
                self.stdouthelper.print_green(location_msg)

                for q in located_questions.qs:
                    question_msg = _create_question_msg(question=q)
                    self.stdouthelper.print_yellow(question_msg)

    def show_report_after_commit(self, result: ReportAfterCommit):
        if result.new_num:
            self._show_summary('新增', result.new_num)
        if result.reviewed_num:
            self._show_summary('复习', result.reviewed_num)
        if result.paused_num:
            self._show_summary('暂停', result.paused_num)
        self._show_need_reviewed_info(result)

    def _show_summary(self, action, total):
        self.stdouthelper.print_blue(
            '\n{}了 {} 个问题'.format(action, total))

    def show_error(self, exc: UserError = None, msg=''):
        if exc:
            assert msg is '', '不能同时传递2个参数'
            self.stdouthelper.print_red('\n{}\n'.format('\n'.join(exc.message)))
        elif msg:
            self.stdouthelper.print_red('\n{}\n'.format(msg))
