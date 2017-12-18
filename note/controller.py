import sys

import note
from note.infrastructure import config
from note.infrastructure.error import UserError
from note.utils.pattern import Singleton


class Controller(metaclass=Singleton):
    def __init__(self, view, logger, parser, get_runner, get_initializer,
                 get_purger, get_status_result_visitor,
                 get_commit_result_visitor):

        self.view = view
        self.logger = logger
        self.parser = parser

        self.get_runner = get_runner
        self.get_initializer = get_initializer
        self.get_purger = get_purger
        self.get_commit_result_visitor = get_commit_result_visitor
        self.get_status_result_visitor = get_status_result_visitor

    def run(self, args=None):
        try:
            self._run(args)
        except UserError as err:
            self.view.show_error(exc=err)
        except SystemExit:
            raise
        except:
            self.logger.critical('', exc_info=True)
            self.view.show_error(msg='sorry,程序发生了内部错误')
            raise SystemExit

    def _run(self, args):
        # 如果是--help，会在此处会向stdout输出信息并且抛出exit程序
        args = self.parser.parse_args(args or sys.argv[1:])

        if args.doc:
            self._show_doc()
        elif args.version:
            self.view.show(note.__version__)
        elif args.cmd:
            self._handle_sub_command(args)
        else:
            self.view.show(
                "see '{} --help'".format(config.APP_NAME))

    @staticmethod
    def _show_doc():
        import webbrowser
        webbrowser.open(config.DOC_URL)

    def _handle_sub_command(self, args):
        if args.cmd == 'init':
            initializer = self.get_initializer()
            initializer.init()
        elif args.cmd == 'status':
            runner = self.get_runner()
            result = runner.run(commit=False, use_link=not args.not_link, short=args.short)
            report = result.accept(self.get_status_result_visitor())
            self.view.show_report_after_status(report)
        elif args.cmd == 'commit':
            runner = self.get_runner()
            result = runner.run(commit=True, time=args.time, use_link=not args.not_link,
                                short=args.short)
            report = result.accept(self.get_commit_result_visitor())
            self.view.show_report_after_commit(report)
        elif args.cmd == 'purge':
            purger = self.get_purger()
            path = args.path
            purger.purge(path)
        else:
            raise RuntimeError
