"""
用于定位性能瓶颈
"""
import cProfile
import os
import pstats
import shutil
import sys
from unittest.mock import patch

try:
    DIR_PATH = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(os.path.dirname(DIR_PATH))
    sys.path.insert(0, ROOT_DIR)
finally:
    from note.utils.os.fs import virtual_workspace
    from note.utils import suppress_stdout, timeit
    from note.__main__ import run as run_note


def sandbox(func):
    def wrap(*args, **kwargs):
        if os.path.exists('sandboxBAK'):
            if os.path.exists('sandbox'):
                shutil.rmtree('sandbox')
            os.rename('sandboxBAK', 'sandbox')

        with virtual_workspace('sandbox') as path:
            with patch('os.getcwd', return_value=path):
                func(*args, **kwargs)

    return wrap


def profile_run(*args):
    with suppress_stdout():
        cProfile.run('time_run()'.format(*args), 'prof.txt')
    p = pstats.Stats("prof.txt")
    p.sort_stats('time').print_stats()


@sandbox
def time_run(*args):
    run_note_ = timeit(run_note)
    with suppress_stdout():
        run_note_(args)
    print('{}:{}'.format(args, run_note_.time))


def run_all():
    time_run()
    time_run('--help')
    time_run('status')


if __name__ == '__main__':
    profile_run()
