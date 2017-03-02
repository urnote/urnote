from note.module.element import QA, QAState
from note.utils.pattern import Singleton


class PurgeQAHandler(metaclass=Singleton):
    @staticmethod
    def handle(qa: QA):
        qa.state = QAState.NORMAL
