from note.module.element import QAState, QA, StateTransition, Command
from note.module.reviewer import Reviewer
from note.utils.pattern import Singleton
from note.utils.review_algorithm import Grade


class ReviewQAHandler(metaclass=Singleton):
    def __init__(self, reviewer: Reviewer):
        self._reviewer = reviewer

    def handle(self, qa, commit, time=None) -> StateTransition:
        """
        处理一个QA,返回处理过后发生的状态转变和问题QA是否被修改的元组
        """
        if qa.state == QAState.NORMAL:
            state_transition, modified = self._handle_normal(commit, qa, time)
        elif qa.state == QAState.OLD:
            state_transition, modified = self._handle_old(qa)
        elif qa.state == QAState.NEED_REVIEWED:
            state_transition, modified = self._handle_need_reviewed(commit, qa,
                                                                    time)
        elif qa.state == QAState.PAUSED:
            state_transition, modified = self._handle_paused(commit, qa)
        else:
            raise RuntimeError

        return state_transition, modified

    def _handle_normal(self, commit, qa, time):
        if qa.command is not None:
            modified = False
            if commit:
                id_ = self._reviewer.new(interval=qa.arg, time=time)
                qa.state, qa.id = QAState.OLD, id_
                qa.command = None
                qa.arg = None
                modified = True
            return StateTransition.NEW_TO_OLD, modified
        return None, False

    # 需要复习的不关心commit,总是会自动转换
    def _handle_old(self, qa: QA):
        id_ = qa.id
        if self._reviewer.need_review(id_):
            qa.state = QAState.NEED_REVIEWED
            return StateTransition.OLD_TO_NEED_REVIEWED, True
        return None, False

    def _handle_need_reviewed(self, commit, qa, time):
        modified = False
        if qa.command == Command.REMEMBER:
            grade = Grade.EASY
        elif qa.command == Command.FORGET:
            grade = Grade.FORGOTTEN
        elif qa.command == Command.PAUSE:
            if commit:
                qa.state = QAState.PAUSED
                qa.command = None
                modified = True
            return StateTransition.NEED_REVIEWED_TO_PAUSED_OLD, modified
        else:
            return StateTransition.STILL_NEED_REVIEWED, modified
        if commit:
            self._reviewer.review(qa.id, grade, time=time)
            qa.state = QAState.OLD
            qa.command = None
            modified = True
        return StateTransition.NEED_REVIEWED_TO_OLD, modified

    @staticmethod
    def _handle_paused(commit, qa):
        if qa.command is not None:
            # 如果命令不是空的,那么只能是继续复习命令,对于继续复习的,直接将其恢复到
            # 加入时的状态(NEED_REVIEWED)即可
            if commit:
                qa.state = QAState.NEED_REVIEWED
                qa.command = None
                return StateTransition.PAUSED_TO_NEED_REVIEWED, True
            else:
                return StateTransition.PAUSED_TO_NEED_REVIEWED, False
        return None, False
