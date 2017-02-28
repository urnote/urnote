import colorama

from note.infrastructure import stdouthelper
from note.infrastructure.error import UserError
from note.module.element import RunResult


class RunResultView:
    def __init__(self):
        # 控制台的字体颜色初始化
        colorama.init()

    def show_run_result(self, result: RunResult):
        self._show_new_info(result)
        self._show_reviewed_info(result)
        self._show_need_reviewed_info(result)
        self._show_paused_info(result)

    @staticmethod
    def _show_paused_info(result):
        if result.paused_num:
            stdouthelper.print_blue(
                '\n{} 个问题暂停复习\n'.format(result.paused_num))

    @staticmethod
    def _show_need_reviewed_info(result):
        if result.need_reviewed_num:
            stdouthelper.print_blue(
                '\n{} 个问题需要复习\n'.format(result.need_reviewed_num))

    @staticmethod
    def _show_reviewed_info(result):
        if result.reviewed_num:
            stdouthelper.print_blue(
                '\n本次复习了 {} 个问题:\n'.format(result.reviewed_num))
            for group in result.reviewed_qs_each_file:
                relative_path, reviewed_qs = (
                    group.relative_path, group.questions)
                stdouthelper.print_green(
                    '    {relative_path}:\n'.format(
                        relative_path=relative_path))
                for reviewed_q in reviewed_qs:
                    stdouthelper.print_yellow(
                        '    {:4}{}\n'.format('', reviewed_q))

    @staticmethod
    def _show_new_info(result):
        if result.new_num:
            stdouthelper.print_blue(
                '\n本次新增 {} 个问题:\n'.format(result.new_num))
            for group in result.new_qs_each_file:
                relative_path, new_qs = group.relative_path, group.questions
                stdouthelper.print_green(
                    '    {relative_path}:\n'.format(
                        relative_path=relative_path))
                for new_q in new_qs:
                    stdouthelper.print_yellow('    {:4}{}\n'.format('', new_q))

    @staticmethod
    def show_error(exc: UserError = None, msg=''):
        if exc:
            stdouthelper.print_red('\n{}\n'.format('\n'.join(exc.message)))
        elif msg:
            stdouthelper.print_red('\n{}\n'.format(msg))

    @staticmethod
    def show_prompt(msg):
        stdouthelper.print_white('\n{}\n'.format(msg))

    @staticmethod
    def show_doc(doc):
        stdouthelper.print_white(doc)
