from note.infrastructure.error import CMDError
from note.module.element import QuestionGroup, RunResult, StateTransition
from note.module.filehandler import WorkspaceManager
from note.module.qahandler.purgeqahandler import PurgeQAHandler
from note.module.qahandler.reviewqahandler import ReviewQAHandler
from note.utils.os import fs
from note.utils.pattern import Singleton


class Initializer(metaclass=Singleton):
    def __init__(self, work_space_manger: WorkspaceManager):
        self._work_space_manger = work_space_manger

    def init(self):
        self._work_space_manger.create_workspace()


class Runner(metaclass=Singleton):
    def __init__(self, qa_handler: ReviewQAHandler,
                 workspace_manger: WorkspaceManager, get_content_handler):
        self._qa_handler = qa_handler
        self._workspace_manger = workspace_manger
        self._get_content_handler = get_content_handler

    def run(self, commit=True, time=None):
        fs.clean_dir(self._workspace_manger.path_helper.task_path)
        return self._handle_each_file(commit, time)

    def _handle_each_file(self, commit, time):
        result = RunResult()
        for relpath, abspath in self._workspace_manger.get_paths():
            content_handler = self._get_content_handler(abspath, relpath)
            qas = list(content_handler.get_qas())

            # 新添加的question和复习了的question
            new_qs = []
            reviewed_qs = []
            for qa in qas:
                state_transition = self._qa_handler.handle(qa, commit, time)
                if state_transition == StateTransition.NEW_TO_OLD:
                    new_qs.append(str(qa))
                elif state_transition in (
                        StateTransition.TO_NEED_REVIEWED,
                        StateTransition.STILL_NEED_REVIEWED):
                    result.need_reviewed_num += 1
                    self._workspace_manger.create_shortcut(abspath)
                elif state_transition == StateTransition.NEED_REVIEWED_TO_OLD:
                    reviewed_qs.append(str(qa))
                elif state_transition == \
                        StateTransition.NEED_REVIEWED_TO_PAUSED_OLD:
                    result.paused_num += 1
                else:
                    pass

            result.add_new_qs(QuestionGroup(relpath, new_qs))
            result.add_reviewed_qs(QuestionGroup(relpath, reviewed_qs))

            content_handler.save_qas(qas)

        return result


class Purger(metaclass=Singleton):
    """
    Raises:
        CMDError :不在工作空间执行或者工作空间根目录下已经有非空purge文件夹
    """

    def __init__(self, qa_handler: PurgeQAHandler,
                 workspace_manger: WorkspaceManager, get_content_handler):
        self._qa_handler = qa_handler
        self._workspace_manger = workspace_manger
        self._get_content_handler = get_content_handler

    def purge(self, path):
        """处理指定path目录中的,将其输出到工作空间当前目录下

        Args:
            path: 目标路径,可以是该工作空间下文件的绝对路径,也可以是相对根目录
                的相对路径
        """

        abspath = self._workspace_manger.get_abspath(path)

        if abspath:
            self._workspace_manger.create_purge_space()
        else:
            raise CMDError.file_not_in_current_workspace()

        self._workspace_manger.copy_to_purge_dir(abspath)
        self._purge()

    def _purge(self):
        for relpath, path in self._workspace_manger.get_paths_in_purge():
            content_handler = self._get_content_handler(path)
            qas = list(content_handler.get_qas())
            for qa in qas:
                self._qa_handler.handle(qa)
            content_handler.save_qas(qas=qas)
