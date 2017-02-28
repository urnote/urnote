from kit.pattern import Singleton

from note.module.element import QA, QAState


class PurgeQAHandler(metaclass=Singleton):
    @staticmethod
    def handle(qa: QA):
        qa.state = QAState.NORMAL
