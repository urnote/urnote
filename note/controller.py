import sys

import note
from note.infrastructure import config
from note.infrastructure.error import UserError
from note.utils.pattern import Singleton


class Controller(metaclass=Singleton):
    def __init__(self, view, logger, parser, get_runner, get_initializer,
                 get_purger):
        self.view = view
        self.logger = logger
        self.parser = parser

        self.get_runner = get_runner
        self.get_initializer = get_initializer
        self.get_purger = get_purger

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
            self.show_doc()
        elif args.version:
            self.view.show_prompt(note.__version__)
        elif args.cmd:
            self.handle_sub_command(args)
        else:
            self.view.show_prompt(
                "see '{} --help'".format(config.APP_NAME_ABBR))

    def show_doc(self):
        from note.infrastructure.config import DOC_PATH
        with open(DOC_PATH, encoding='utf-8') as fo:
            doc = fo.read()
            self.view.show_doc(doc)

    def handle_sub_command(self, args):
        if args.cmd == 'init':
            initializer = self.get_initializer()
            initializer.init()
        elif args.cmd == 'status':
            runner = self.get_runner()
            result = runner.run(commit=False)
            self.view.show_run_result(result)
        elif args.cmd == 'commit':
            runner = self.get_runner()
            runner.run(commit=True, time=args.time)
        elif args.cmd == 'purge':
            purger = self.get_purger()
            path = args.path
            purger.purge(path)
        else:
            raise RuntimeError
