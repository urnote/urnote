from kit.pattern import Singleton
from kit.review_algorithm import Grade

from note.module.element import QAState, QA, StateTransition, Command
from note.module.reviewer import Reviewer


class ReviewQAHandler(metaclass=Singleton):
    def __init__(self, reviewer: Reviewer):
        self._reviewer = reviewer

    def handle(self, qa, commit, time=None) -> StateTransition:
        state_transition = None
        if qa.state == QAState.NORMAL:
            state_transition = self._handle_normal(commit, qa, time)
        elif qa.state == QAState.OLD:
            state_transition = self._handle_old(qa)
        elif qa.state == QAState.NEED_REVIEWED:
            state_transition = self._handle_need_reviewed(commit, qa, time)
        elif qa.state == QAState.PAUSED:
            state_transition = self._handle_paused(commit, qa)

        return state_transition

    def _handle_normal(self, commit, qa, time):
        if qa.command is not None:
            if commit:
                id_ = self._reviewer.new(interval=qa.arg, time=time)
                qa.state, qa.id = QAState.OLD, id_
                qa.command = None
                qa.arg = None
            return StateTransition.NEW_TO_OLD

    # 需要复习的不关心commit,总是会自动转换
    def _handle_old(self, qa: QA):
        id_ = qa.id
        if self._reviewer.need_review(id_):
            qa.state = QAState.NEED_REVIEWED
            return StateTransition.TO_NEED_REVIEWED

    def _handle_need_reviewed(self, commit, qa, time):
        if qa.command == Command.YES:
            grade = Grade.EASY
        elif qa.command == Command.NO:
            grade = Grade.FORGOTTEN
        elif qa.command == Command.PAUSE:
            if commit:
                qa.state = QAState.PAUSED
                qa.command = None
            return StateTransition.NEED_REVIEWED_TO_PAUSED_OLD
        else:
            return StateTransition.STILL_NEED_REVIEWED
        if commit:
            self._reviewer.review(qa.id, grade, time=time)
            qa.state = QAState.OLD
            qa.command = None
        return StateTransition.NEED_REVIEWED_TO_OLD

    def _handle_paused(self, commit, qa):
        if qa.command is not None:
            if commit:
                qa.state = QAState.OLD
                qa.command = None
                return self._handle_old(qa)
            else:
                transition = self._handle_old(qa)
                qa.state = QAState.PAUSED
                return transition
