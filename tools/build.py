"""
使用PyInstaller生成exe
"""
import os
import platform

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
            'bat_path': join_path('tools', 'SET_PATH.bat'),
            'main_module_path': join_path('note', '__main__.py'),
            'python_search_path': join_path('note'),
            'icon_path': join_path('tools', 'one_note.ico')
        }
        if platform.system() == 'Windows':
            kwargs['bat_path'] = join_path('tools', 'SET_PATH.bat')
        elif platform.system() == 'Linux':
            kwargs['bat_path'] = join_path('tools', 'install.sh')
        else:
            raise NotImplementedError('暂不支持Windows和Linux以外的系统')

        content = content.format(**kwargs)
    with open('main.spec', 'w') as fo:
        fo.write(content)
    __main__.run(['main.spec', '-y'])
    os.remove('main.spec')


if __name__ == '__main__':
    main()
