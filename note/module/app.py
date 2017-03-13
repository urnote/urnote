from note.infrastructure.error import CMDError
from note.module.element import (AllNoteHandleResults, StateTransition,
                                 OneNoteHandleResult)
from note.module.filehandler import WorkspaceManager
from note.module.qahandler.purgeqahandler import PurgeQAHandler
from note.module.qahandler.reviewqahandler import ReviewQAHandler
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
        self._workspace_manger.clean_task_dir()
        return self._handle_all(commit, time)

    def _handle_all(self, commit, time):
        results = AllNoteHandleResults()
        for abspath in self._workspace_manger.get_paths():
            result = self._handle_one(abspath, commit, time)
            if result:
                results.add(result)
        return results

    def _handle_one(self, abspath, commit, time):
        content_handler = self._get_content_handler(
            abspath, self._workspace_manger.get_relpath(abspath))
        qas = list(content_handler.get_qas())

        new_qs = []
        need_reviewed_qs = []
        reviewed_qs = []
        paused_qs = []

        for qa in qas:
            state_transition = self._qa_handler.handle(qa, commit, time)
            if state_transition == StateTransition.NEW_TO_OLD:
                new_qs.append(str(qa))
            elif state_transition in (
                    StateTransition.OLD_TO_NEED_REVIEWED,
                    StateTransition.STILL_NEED_REVIEWED):
                need_reviewed_qs.append(str(qa))
                self._workspace_manger.create_shortcut(abspath)
            elif state_transition == StateTransition.NEED_REVIEWED_TO_OLD:
                reviewed_qs.append(str(qa))
            elif state_transition == \
                    StateTransition.NEED_REVIEWED_TO_PAUSED_OLD:
                paused_qs.append(str(qa))
            else:
                pass

        content_handler.save_qas(qas)

        if any((new_qs, need_reviewed_qs, reviewed_qs, paused_qs)):
            result = OneNoteHandleResult(
                location=self._workspace_manger.get_relpath(abspath),
                new_qs=new_qs,
                need_reviewed_qs=need_reviewed_qs,
                reviewed_qs=reviewed_qs,
                paused_qs=paused_qs)
            return result
        return None


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
        for abspath in self._workspace_manger.get_paths_in_purge():
            content_handler = self._get_content_handler(abspath)
            qas = list(content_handler.get_qas())
            for qa in qas:
                self._qa_handler.handle(qa)
            content_handler.save_qas(qas=qas)
