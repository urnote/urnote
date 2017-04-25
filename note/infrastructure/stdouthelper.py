"""
提供对于显示到控制台的信息的颜色控制
"""

import sys

import colorama
from colorama import Fore

_STDOUT_ENCODE = sys.stdout.encoding


class StdoutHelper:
    def __init__(self):
        colorama.init()

    @staticmethod
    def _print(flag, message):
        message = message.encode(
            _STDOUT_ENCODE, 'ignore').decode(_STDOUT_ENCODE)
        sys.stdout.write('{}{}'.format(flag, message))

    def print(self, message):
        self._print(Fore.RESET, message)

    def print_green(self, message):
        self._print(Fore.GREEN, message)

    def print_yellow(self, message):
        self._print(Fore.YELLOW, message)

    def print_red(self, message):
        self._print(Fore.RED, message)

    def print_blue(self, message):
        self._print(Fore.CYAN, message)
