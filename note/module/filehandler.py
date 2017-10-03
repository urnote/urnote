import os
import pickle
import shutil

from note.infrastructure import config
from note.infrastructure.error import CMDError
from note.module.pathhelper import PathHelper
from note.utils.os import fs
from note.utils.pattern import Singleton


class FileContentHandler:
    """
    Raises:
        FileContentError: 调用get_qas方法时可能抛出的异常
    """

    def get_qas(self):
        """返回从文件中内容中解析出来的QA对象列表"""

    def save_qas(self, qas):
        """保存qa列表到文件"""


class WorkspaceOperationRecord(object):
    def __init__(self):
        self.last_operation_in_task_dir = None
        self.copy_map = {}


class WorkspaceManager(metaclass=Singleton):
    """
    负责处理所有和项目文件相关的任务,包括文件操作历史等
    
    TODO: 不应该暴露绝对路径出去，只给相对路径，外部也不应该绕过该类直接访问文件．
    """

    def __init__(self, path_helper: PathHelper):
        self._path = None
        self._file_handler = None
        self.path_helper = path_helper

    def get_paths(self):
        """返回工作空间中的笔记的路径"""
        for abspath in fs.walk(
                dirpath=self.path_helper.root_dir,
                ignore_patterns=config.IGNORE_FILES,
                ignore_patterns_filepath=self.path_helper.ignore_path):
            yield abspath

    def get_paths_in_taskdir(self):
        """返回工作空间中的笔记的路径"""
        for abspath in fs.walk(
                dirpath=self.path_helper.task_path,
                ignore_patterns=config.IGNORE_FILES,
                ignore_patterns_filepath=self.path_helper.ignore_path):
            yield abspath

    def get_relpath(self, path):
        """得到path在工作空间下的相对路径"""
        return os.path.relpath(path, self.path_helper.root_dir)

    def create_shortcut(self, path):
        """在TASK目录下面创建快捷方式,如果需要目录则自动创建"""
        fs.create_shortcut(path, self.path_helper.task_path, keep_dir=True)

        wor = None
        try:
            with open(self.path_helper.workspace_operation_record_path, 'rb')as fo:
                wor = pickle.load(fo)
        except OSError:
            wor = WorkspaceOperationRecord()
        finally:
            wor.last_operation_in_task_dir = 'create_shortcut'
            with open(self.path_helper.workspace_operation_record_path, 'wb')as fo:
                pickle.dump(wor, fo)

    def copy_to_task_dir(self, abspath):
        fs.copy_file(abspath, self.path_helper.task_path, keep_dir=True)

        try:
            with open(self.path_helper.workspace_operation_record_path, 'rb')as fo:
                wor = pickle.load(fo)
        except OSError:
            wor = WorkspaceOperationRecord()

        wor.last_operation_in_task_dir = 'copy'
        with open(self.path_helper.workspace_operation_record_path, 'wb')as fo:
            pickle.dump(wor, fo)

    def last_task_operation(self):
        try:
            with open(self.path_helper.workspace_operation_record_path, 'rb')as fo:
                wor = pickle.load(fo)
                return wor.last_operation_in_task_dir
        except OSError:
            return None

    def move_back_to_root_dir(self):
        with open(self.path_helper.workspace_operation_record_path, 'rb')as fo:
            wor = pickle.load(fo)
            assert wor.last_operation_in_task_dir == 'move'

            for target_path, src_path in wor.copy_map.items():
                shutil.move(target_path, src_path)

        with open(self.path_helper.workspace_operation_record_path, 'wb')as fo:
            pickle.dump(WorkspaceOperationRecord(), fo)

    def create_workspace(self, path=None):
        """创建工作空间
        Args:
            path: 在path目录下建立工作空间,默认为当前工作空间
        """
        if self.path_helper.root_dir:
            raise CMDError.duple_init(root_dir=self.path_helper.root_dir)
        path_helper = PathHelper()
        if path is None:
            path_helper.root_dir = os.getcwd()
        else:
            path_helper.root_dir = path

        params = (
            ((path_helper.app_date_path,), {'is_dir': True}),
            ((path_helper.task_path,), {'is_dir': True}),
            ((path_helper.db_path,), {}),
            ((path_helper.log_path,), {}),
            ((path_helper.user_config_path,), {}),
            ((path_helper.ignore_path,), {}),
            ((path_helper.workspace_operation_record_path,), {})
        )
        for args, kwargs in params:
            self._create(*args, **kwargs)

        fs.hidden_dir(path_helper.app_date_path)
        with open(path_helper.workspace_operation_record_path, 'wb')as fo:
            pickle.dump(WorkspaceOperationRecord(), fo)

        self.path_helper = path_helper

    @staticmethod
    def _create(path, is_dir=False):
        if not os.path.exists(path):
            if is_dir:
                os.mkdir(path)
            else:
                open(path, 'w').close()
        else:
            raise RuntimeError

    def have_workspace(self):
        """判断是否找到了工作空间"""
        return True if self.path_helper.root_dir else False

    def get_abspath(self, path):
        """得到path的绝对路径,path可以是相对路径或者绝对路径,并且必须在工作空间中

        Returns: 返回资源绝对路径,可能是文件路径,也可能是目录,如果不存在返回None
        """
        # 处理相对路径
        if not os.path.isabs(path):
            path = path.abspath(path, self.path_helper.root_dir)

        # 路径不在文件系统上或者不在工作空间下
        if not path.startswith(self.path_helper.root_dir) or not os.path.exists(
                path):
            return

        return path

    def create_purge_space(self):
        """准备好PURGE目录,用于存放Purge结果"""
        if os.path.exists(self.path_helper.purge_path):
            if len(os.listdir(self.path_helper.purge_path)):
                raise CMDError.purge_exist_but_not_empty()
        else:
            os.mkdir(self.path_helper.purge_path)
        return self.path_helper.purge_path

    def copy_to_purge_dir(self, abspath):
        """
        将abspath指向的文件或目录拷贝到purge目录下,拷贝过程中忽略
        config.IGNORE_FILES中的目录
        """
        ignore = shutil.ignore_patterns(*config.IGNORE_FILES)
        if os.path.isdir(abspath):
            shutil.copytree(abspath, self.path_helper.purge_path, ignore=ignore)
        else:
            ignores = ignore(None, abspath)
            if not ignores:
                shutil.copy(abspath, self.path_helper.purge_path)

    def get_paths_in_purge(self):
        """返回工作空间中的笔记的路径"""
        for abspath in fs.walk(
                dirpath=self.path_helper.root_dir,
                ignore_patterns=config.IGNORE_FILES,
                ignore_patterns_filepath=self.path_helper.ignore_path):
            yield abspath

    def clean_task_dir(self):
        fs.clean_dir(self.path_helper.task_path)
