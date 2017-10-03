"""该模块主要提供一些关于文件系统(filesystem)的API"""
import difflib
import filecmp
import os
import platform
import shutil
from contextlib import ContextDecorator
from filecmp import dircmp
from functools import wraps

__all__ = [
    'create_shortcut', 'create_shortcut_on_windows', 'create_shortcut_on_linux',
    'hidden_dir', 'hidden_dir_on_windows', 'hidden_dir_on_linux',
    'make_dir_of_file', 'clean_dir', 'exist_in_dir', 'exist_in_or_above',
    'walk', 'virtual_workspace', 'is_same'
]


def create_shortcut(src_path, dest_dir, keep_dir=False):
    return {
        'Windows': create_shortcut_on_windows,
        'Linux': create_shortcut_on_linux
    }[platform.system()](src_path, dest_dir, keep_dir)


def create_shortcut_on_windows(src_path, dest_dir, keep_dir=False):
    """在windows平台下创建指定路径的快捷方式,快捷方式的名字和前者一样

    eg:
        create_shortcut_2('C:/hello/world/python.exe','D:/programs')
        将在D:/programs 目录下创建python.lnk快捷方式
    """
    # noinspection PyUnresolvedReferences
    import win32com.client

    assert platform.system() == 'Windows'

    filename = os.path.basename(src_path)
    filename = os.path.splitext(filename)[0] + '.lnk'
    link_path = os.path.join(dest_dir, filename)

    if not link_path.endswith(".lnk"):
        raise Exception("快捷方式路径名称需以 .lnk 或 .url 结尾")

    dir_path, file_name = os.path.split(src_path)
    name, ext = os.path.splitext(file_name)
    name += '.lnk'

    ws = win32com.client.Dispatch("wscript.shell")
    shortcut = ws.CreateShortcut(link_path)
    shortcut.TargetPath = src_path
    shortcut.Arguments = '-m idlelib.idle'
    shortcut.Save()


def create_shortcut_on_linux(src_path, dest_dir, keep_dir=False):
    """在dest_dir目录下创建快捷方式
    src_path和dest_dir可以使用相对路径和绝对路径。dest_dir必须存在，不存在会跑出异常。
    """
    assert platform.system() == 'Linux'
    if keep_dir:
        root_dir = os.path.commonpath([os.path.abspath(src_path), os.path.abspath(dest_dir)])
        link_path = os.path.join(dest_dir, os.path.relpath(src_path, root_dir))
        crete_dir_if_not_exist(link_path)
    else:
        _, basename = os.path.split(src_path)
        link_path = os.path.join(dest_dir, basename)
    os.symlink(src_path, link_path)


def crete_dir_if_not_exist(path):
    dirname = os.path.dirname(os.path.abspath(path))
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def hidden_dir(dirpath):
    return {
        'Windows': hidden_dir_on_windows,
        'Linux': hidden_dir_on_linux
    }[platform.system()](dirpath)


def hidden_dir_on_windows(dirpath):
    """用于在windows操作系统下隐藏目录"""
    assert platform.system() == 'Windows'

    import ctypes

    file_attribute_hidden = 0x02

    ret = ctypes.windll.kernel32.SetFileAttributesW(dirpath,
                                                    file_attribute_hidden)

    # return code of zero indicates failure, raise Windows error
    if not ret:
        raise ctypes.WinError()


def hidden_dir_on_linux(dirpath):
    dirname, basename = os.path.split(dirpath)
    if basename[0] == '.':
        pass
    else:
        os.rename(dirpath, os.path.join(dirname, '.' + basename))


def make_dir_of_file(filepath):
    """创建path路径的目录

    例如:
        E:\A\b.py 创建A目录

    Args:
        filepath: 文件路径
    """
    assert filepath.endwith('\\') is False
    assert filepath.endwith('/') is False

    dirpath = os.path.dirname(filepath)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def clean_dir(dir_path):
    """清空目录里面的所有文件和子目录

    和Python内置删除目录的区别如下:
        os.rmdir只能删除空目录
        shutil.rmtree删除非空目录,但是会连跟目录一并删除
    """
    if os.path.isdir(dir_path):
        paths = os.listdir(dir_path)
        for path in paths:
            filepath = os.path.join(dir_path, path)
            if os.path.isfile(filepath):
                try:
                    os.remove(filepath)
                except os.error:
                    raise
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath, True)
        return
    raise OSError('{}不是一个目录'.format(dir_path))


def exist_in_dir(dirpath, name):
    """判断一个目录或文件是否存在于另一个目录下

    Args:
        dirpath: 判断的路径,采取绝对路径
        name: 判断是否存在的目录名或文件名

    Returns:
        如果存在,返回绝对路径,如果不存在,返回None
    """
    assert os.path.isabs(dirpath) is True
    assert os.path.isabs(name) is False

    if not os.path.isdir(dirpath):
        raise OSError('{}不是一个有效的目录'.format(dirpath))

    name = os.path.join(dirpath, name)
    if os.path.exists(name):
        return name
    else:
        return None


def exist_in_or_above(dirpath, name):
    """判断一个目录是否在当前目录或者祖先目录中存在

    Args:
        dirpath: 起始目录路径
        name: 将要判断是否存在的目录名或文件名

    Returns:
        如果找到了,返回找到的目录路径,以\结尾,如果没有找到,返回None
    """
    assert os.path.isabs(dirpath) is True
    assert os.path.isabs(name) is False

    while 1:
        try:
            target_path = exist_in_dir(dirpath, name)
        except OSError:
            raise

        if target_path:
            return target_path
        else:
            # 不存在就继续往上找
            dirpath = os.path.dirname(dirpath)
            if os.path.ismount(dirpath):
                return None


def walk(dirpath, ignore_patterns: tuple = (), ignore_patterns_filepath=''):
    """返回一个目录中没有被忽略的文件的路径

    Args:
        ignore_patterns: 忽略的模式.
            可以使用下面的3种类型:
                .idea/          idea目录
                *.txt           后缀名为txt
                其他            全名匹配
        dirpath: 目标目录路径
        ignore_patterns_filepath: 忽略模式文件的路径,该文件中每行表示一个模式,#开头的表示注释行

    Yields:
        完整的路径
    """
    if ignore_patterns_filepath != '':
        with open(ignore_patterns_filepath, 'r', encoding='utf-8') as fo:
            lines = fo.readlines()
            lines = map(lambda line: line.strip(), lines)
            lines = filter(lambda line: line.startswith('#') is False, lines)
            lines = filter(lambda line: line != '', lines)
            ignore_patterns += tuple(lines)

    ignore_dirnames, ignore_extnames, ignore_filenames = _parser(
        ignore_patterns)

    for dirpath, dirnames, filenames in os.walk(dirpath):
        for dirname in set(dirnames) & set(ignore_dirnames):
            dirnames.remove(dirname)

        # 接下来开始处遍历文件
        for filename in filenames:
            if filename in ignore_filenames:
                continue
            else:
                # 只有split之后长度大于1 才表示有后缀
                # [-1]位置扩展名如果在忽略列表则忽略
                res = filename.split('.')
                if len(res) > 1 and res[-1].strip() in ignore_extnames:
                    continue
                else:
                    yield os.path.join(dirpath, filename)


def _parser(ignore_patterns):
    """拿到忽略模式列表中的目录名,后缀名,全名"""
    dirnames = []
    filenames = []
    extnames = []

    for item in ignore_patterns:
        if item.endswith('/') or item.endswith('\\'):
            dirnames.append(item[:-1])
        else:
            res = item.split('.')
            if len(res) == 2:
                name = res[0].strip()
                ext = res[-1].strip()
                if name == '*':
                    extnames.append(ext)
                    continue
            filenames.append(item)
    return set(dirnames), set(extnames), set(filenames)


class virtual_workspace(ContextDecorator):
    """创建一个虚拟空间,之后在虚拟空间做的任何操作都会还原到初始状态

    原理:
        备份该目录到父目录下,如果没有权限将报错,执行完代码之后,将备份的目录还原即可(重命名目录).

    Args:
        dirname: 目录名,可以是相对路径和绝对路径

    Raises:
        FileNotFoundError: dir_path 不存在
        OSError: 备份的目标目录已经存在
    """

    def __init__(self, dirname):
        self.dirname = os.path.abspath(dirname)
        self.bak_dirname = os.path.abspath(self.dirname + 'BAK')

    def enter(self):
        self.dirname = self.dirname.rstrip(r'\/')
        if not os.path.isdir(self.dirname):
            raise NotADirectoryError(self.dirname)
        if not os.path.exists(self.dirname):
            raise FileNotFoundError(self.dirname)

        if os.path.exists(self.bak_dirname):
            raise FileExistsError(self.bak_dirname)

        shutil.copytree(self.dirname, self.bak_dirname)
        return self.dirname

    def exit(self):
        if os.path.exists(self.dirname):
            shutil.rmtree(self.dirname)
        os.rename(self.bak_dirname, self.dirname)

    def __enter__(self):
        return self.enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return inner


def copy_file(src_path, dest_dir, keep_dir):
    if keep_dir:
        root_dir = os.path.commonpath([os.path.abspath(src_path), os.path.abspath(dest_dir)])
        target_path = os.path.join(dest_dir, os.path.relpath(src_path, root_dir))
        crete_dir_if_not_exist(target_path)
    else:
        _, basename = os.path.split(src_path)
        target_path = os.path.join(dest_dir, basename)

    shutil.copyfile(src_path, target_path)
    return target_path


def move_file(src_path, dest_dir, keep_dir):
    if keep_dir:
        root_dir = os.path.commonpath([os.path.abspath(src_path), os.path.abspath(dest_dir)])
        target_path = os.path.join(dest_dir, os.path.relpath(src_path, root_dir))
        crete_dir_if_not_exist(target_path)
    else:
        _, basename = os.path.split(src_path)
        target_path = os.path.join(dest_dir, basename)

    shutil.move(src_path, target_path)
    return target_path


def is_same(dir1, dir2, **kwargs):
    """
    Compare two directory trees content.
    Return False if they differ, True is they are the same.
    """
    compared = dircmp(dir1, dir2, **kwargs)
    if (compared.left_only or compared.right_only or compared.diff_files
        or compared.funny_files):
        return False
    for subdir in compared.common_dirs:
        if not is_same(os.path.join(dir1, subdir), os.path.join(dir2, subdir), **kwargs):
            return False
    return True


def _dir_cmp(cmp, raise_exc=True):
    if cmp.diff_files:
        for file in cmp.diff_files:
            with open(os.path.join(cmp.left, file), 'r') as left_fo, open(
                    os.path.join(cmp.right, file), 'r') as right_fo:
                left = left_fo.readlines()
                right = right_fo.readlines()
                d = difflib.Differ()
                diff = d.compare(left, right)
                print('\n'.join(list(diff)))
        if raise_exc:
            raise ValueError(cmp.diff_files)
        else:
            return False
    for sub_cmp in cmp.subdirs.values():
        if not _dir_cmp(sub_cmp):
            return False
    else:
        return True


def is_same2(dir1, dir2, raise_exc=True, **kwargs):
    """
    Compare two directory trees content. Only compare files in both directories.
    Return False if they differ, True is they are the same.
    """
    cmp = filecmp.dircmp(dir1, dir2, **kwargs)
    return _dir_cmp(cmp, raise_exc)
