"""
使用PyInstaller生成exe
"""
import os

from PyInstaller import __main__

# noinspection PyUnresolvedReferences
import context

from note.infrastructure import config

assert config.DEBUG is False


def join_path(*args):
    path = os.path.join(ROOT_DIR, *args)
    return os.path.normpath(path)


ROOT_DIR = os.path.dirname(os.path.dirname(__file__))


def main():
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


if __name__ == '__main__':
    main()
