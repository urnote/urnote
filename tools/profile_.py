"""
用于定位性能瓶颈
"""
import cProfile
import os
import pstats
import shutil
from unittest.mock import patch

# noinspection PyUnresolvedReferences
import context
from note.__main__ import run as run_note
from note.infrastructure import config
from note.utils import suppress_stdout, timeit
from note.utils.os.fs import virtual_workspace


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


@sandbox
def profile_run(*args):
    # with suppress_stdout():
    cProfile.run('run_note({})'.format(args), 'prof.txt')
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


def profile_memory(*args):
    import objgraph
    run_note(args)
    objgraph.show_most_common_types(limit=30)
    # objgraph.show_refs([controller], max_depth=6)


@sandbox
def run(*args):
    run_note(args)


if __name__ == '__main__':
    assert config.DEBUG is True
    run()
