import argparse
import sys

from note.infrastructure.error import ArgParserError


class CustomArgumentParser(argparse.ArgumentParser):
    """重载了ArgumentParser的error处理的Parser

    使用该类创建的parser.对其添加子解析器时也会使用该类
    """

    def __init__(self, *args, **kwargs):
        view = kwargs.get('view')
        if view:
            kwargs.pop('view')
        super().__init__(*args, **kwargs)
        self.view = view

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.

        If you override this in a subclass, it should not return -- it
        should either exit or raise an exception.
        """
        raise ArgParserError(message)

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, self.view)
        sys.exit(status)

    def print_help(self, file=None):
        self.view.show_prompt(self.format_help())
