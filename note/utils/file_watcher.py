import builtins

__all__ = ['watch', 'get_not_closed_files', 'close_all']

_opened_files = set()
_old_open = builtins.open


def _new_open(*args, **kwargs):
    fo = _old_open(*args, **kwargs)
    _opened_files.add(fo)
    return fo


def watch():
    builtins.open = _new_open


def get_not_closed_files():
    return (file for file in _opened_files if not file.closed)


def close_all(echo=False):
    for file in get_not_closed_files():
        if echo:
            print('CLOSE: {}'.format(file.name))
        file.close()
