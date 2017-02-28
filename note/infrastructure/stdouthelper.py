"""
提供对于显示到控制台的信息的颜色控制
"""

import sys

from colorama import Fore

_STDOUT_ENCODE = sys.stdout.encoding


def _print(flag, message):
    message = message.encode(_STDOUT_ENCODE, 'ignore').decode(_STDOUT_ENCODE)
    print('{}{}'.format(flag, message), end='')


def print_white(message):
    _print(Fore.WHITE, message)


def print_green(message):
    _print(Fore.GREEN, message)


def print_yellow(message):
    _print(Fore.YELLOW, message)


def print_red(message):
    _print(Fore.RED, message)


def print_blue(message):
    _print(Fore.CYAN, message)
