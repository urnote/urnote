import os

from kit.cached_property import cached_property
from kit.os.fs import exist_in_or_above
from kit.pattern import Singleton

from note.infrastructure import config


class PathHelper(metaclass=Singleton):
    """
    提供文件的绝对路径以及创建项目的文件结构
    """

    def __init__(self):
        self._root_dir = None
        path = exist_in_or_above(os.getcwd(), config.APP_DATE_DIR_NAME)
        if path:
            # 因为path是目录,结尾以斜杠结尾,所以其父目录需要两次dirname
            dirname = os.path.dirname(path)
            self._root_dir = dirname

    @property
    def root_dir(self):
        return self._root_dir

    @root_dir.setter
    def root_dir(self, value):
        self._root_dir = value

    @cached_property
    def task_path(self):
        return self._join(config.TASK_DIR_NAME)

    @cached_property
    def app_date_path(self):
        return self._join(config.APP_DATE_DIR_NAME)

    @cached_property
    def db_path(self):
        return self._join(config.DB_PATH)

    @cached_property
    def log_path(self):
        return self._join(config.LOG_PATH)

    @cached_property
    def user_config_path(self):
        return self._join(config.CONFIG_PATH)

    @cached_property
    def ignore_path(self):
        return self._join(config.IGNORE_PATH)

    @cached_property
    def purge_path(self):
        return self._join(config.PURGE_DIR_NAME)

    def _join(self, path):
        if self._root_dir:
            return os.path.join(self._root_dir, path)
        else:
            raise FileNotFoundError

    def calc_relpath(self, path):
        """得到path在工作空间下的相对路径"""
        return os.path.relpath(path, self._root_dir)
