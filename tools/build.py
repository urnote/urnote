"""
使用PyInstaller生成exe
"""
import os
import sys

try:
    # noinspection PyUnresolvedReferences
    from note.infrastructure import config
except ImportError:
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, ROOT_DIR)
finally:
    assert config.DEBUG is False

from PyInstaller import __main__


def join_path(*args):
    path = os.path.join(ROOT_DIR, *args)
    return os.path.normpath(path)


ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
with open('main_D.spec.template', 'r') as fo:
    content = fo.read()

    kwargs = {
        'locales_path': join_path('note', 'infrastructure', 'locales'),
        'docs_path': join_path('docs'),
        'bat_path': join_path('tools', 'SET_PATH.bat'),
        'main_module_path': join_path('note', '__main__.py'),
        'python_search_path': join_path('note'),
        'icon_path': join_path('tools', 'one_note.ico')
    }
    content = content.format(**kwargs)

with open('main.spec', 'w') as fo:
    fo.write(content)

__main__.run(['main.spec', '-y'])

os.remove('main.spec')
