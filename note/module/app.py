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


class StatusCMDHandler(metaclass=Singleton):
    def __init__(self, qa_handler: ReviewQAHandler,
                 workspace_manger: WorkspaceManager, get_content_handler):
        self._qa_handler = qa_handler
        self._workspace_manger = workspace_manger
        self._get_content_handler = get_content_handler
        self._last_task_operation = None

    def run(self, commit=True, time=None, use_link=True, short=False, pattern=None, default=None):
        # 处理task空间的内容，返回qa_map,如果没什么处理结果返回{}
        if short:
            use_link = False

        id_qa_mapping = {}
        self._last_task_operation = self._workspace_manger.last_task_operation()
        if self._last_task_operation in ('copy', 'short'):
            for abspath in self._workspace_manger.get_paths_in_taskdir(pattern):
                content_handler = self._get_content_handler(
                    abspath, self._workspace_manger.get_relpath(abspath))
                for qa in content_handler.get_qas():
                    if qa.id:
                        id_qa_mapping[qa.id] = qa
        self._workspace_manger.clean_task_dir()

        # 处理所有的核心笔记的内容，返回结果
        results = AllNoteHandleResults()
        for abspath in self._workspace_manger.get_paths(pattern):
            result = self._handle_one(abspath, commit, time, use_link, short, id_qa_mapping,
                                      default)
            if result:
                results.add(result)
        return results

    def _handle_one(self, abspath, commit, time, use_link, short, id_qa_mapping, default=None):
        location = self._workspace_manger.get_relpath(abspath)
        content_handler = self._get_content_handler(abspath, location)
        qas = list(content_handler.get_qas())

        new_qs = []
        need_reviewed_qs = []
        need_reviewed_qs2 = []
        reviewed_qs = []
        paused_qs = []
        modified = False
        for qa in qas:
            # 合并策略
            qa_in_task = id_qa_mapping.get(qa.id)
            if qa_in_task:
                if self._last_task_operation == 'short':
                    qa_in_task.question = qa_in_task.question.lstrip()[1:]
                if any([qa.question != qa_in_task.question,
                        qa.answer != qa_in_task.answer,
                        qa.command != qa_in_task.command,
                        qa.arg != qa_in_task.arg]):
                    modified = True
                    qa.question = qa_in_task.question
                    qa.answer = qa_in_task.answer
                    qa.command = qa_in_task.command
                    qa.arg = qa_in_task.arg
                if qa_in_task.body:
                    if qa.body != qa_in_task.body:
                        modified = True
                        qa.body = qa_in_task.body

            if qa.command is None and default:
                try:
                    qa.command = default
                except ValueError:
                    pass
                else:
                    if commit:
                        modified = True
            state_transition, modified_ = self._qa_handler.handle(qa, commit, time)
            modified = modified or modified_

            if state_transition == StateTransition.NEW_TO_OLD:
                new_qs.append(str(qa))
            elif state_transition in (
                    StateTransition.OLD_TO_NEED_REVIEWED,
                    StateTransition.STILL_NEED_REVIEWED,
                    StateTransition.PAUSED_TO_NEED_REVIEWED):
                need_reviewed_qs.append(str(qa))
                need_reviewed_qs2.append(qa)
            elif state_transition == StateTransition.NEED_REVIEWED_TO_OLD:
                reviewed_qs.append(str(qa))
            elif state_transition == \
                    StateTransition.NEED_REVIEWED_TO_PAUSED_OLD:
                paused_qs.append(str(qa))
            else:
                pass

        if modified:
            content_handler.save_qas(qas)

        if need_reviewed_qs:
            if use_link:
                self._workspace_manger.create_shortcut(abspath)
            else:
                if short:
                    self._append_review_task_in_task_file(location, need_reviewed_qs2)
                else:
                    self._workspace_manger.copy_to_task_dir(abspath)

        if any((new_qs, need_reviewed_qs, reviewed_qs, paused_qs)):
            result = OneNoteHandleResult(
                location=location,
                new_qs=new_qs,
                need_reviewed_qs=need_reviewed_qs,
                reviewed_qs=reviewed_qs,
                paused_qs=paused_qs)
            return result
        return None

    def _append_review_task_in_task_file(self, location, need_reviewed_qs):
        self._remove_body_in_qas(need_reviewed_qs)
        task_file_path = self._workspace_manger.task_file_path()
        content_handler = self._get_content_handler(
            task_file_path, self._workspace_manger.get_relpath(task_file_path))
        content_handler.append_qas(need_reviewed_qs, location)

    @staticmethod
    def _remove_body_in_qas(qas):
        for qa in qas:
            qa.body = None


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
