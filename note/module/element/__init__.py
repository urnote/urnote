from enum import Enum

from note.utils import Base


class QA(Base):
    __slots__ = ('question', 'answer', 'id', 'state', '_command', 'arg')

    def __init__(self, question='', answer='', id_=None, state=None,
                 command=None, arg=None):
        self.question = question
        self.answer = answer
        self.id = id_
        self.state = state

        # 后面可能跟一部分表示命令的信息,比如评分
        self._command = command
        self.arg = arg

    @property
    def command(self):
        assert self.state != QAState.OLD
        return self._command

    @command.setter
    def command(self, value):
        if value is None:
            self._command = None
            return

        assert self.state is not None
        assert self.state != QAState.OLD
        if self.state == QAState.NORMAL:
            assert value == Command.ADD
        if self.state == QAState.NEED_REVIEWED:
            assert value in (Command.REMEMBER, Command.FORGET, Command.PAUSE)
        if self.state == QAState.PAUSED:
            assert value == Command.CONTINUE

        self._command = value

    def __str__(self):
        """该方法决定了对象的显示字符串,根据情况应该重载"""
        return self.question


class QAState(Enum):
    NORMAL = 0  # 未加入复习计划的
    OLD = 1  # 已加入复习计划的,未到复习时间
    NEED_REVIEWED = 2  # 已加入复习计划的,已经到了复习时间
    PAUSED = 3  # 暂时离开复习计划的


class StateTransition(Enum):
    """程序执行过程中QA可能发生的状态转换

    没有发生转移使用None表示,如OLD_TO_OLD
    """
    NEW_TO_OLD = 0  # 新加入的
    NEED_REVIEWED_TO_OLD = 1  # 复习了的(不是暂停)
    NEED_REVIEWED_TO_PAUSED_OLD = 2  # 暂停了的
    OLD_TO_NEED_REVIEWED = 3  # 本次新加入的需要复习的
    STILL_NEED_REVIEWED = 4  # 表示没有改变，还是需要复习
    PAUSED_TO_NEED_REVIEWED = 5  # 重新加入复习计划


class Command(Enum):
    ADD = 0
    REMEMBER = 1
    FORGET = 2
    PAUSE = 3
    CONTINUE = 4


class OneNoteHandleResult(Base):
    """一个文件处理的结果"""

    def __init__(self, location, new_qs, need_reviewed_qs, reviewed_qs,
                 paused_qs):
        self.location = location
        # 新的question
        self.new_qs = new_qs
        # 需要复习的question
        self.need_reviewed_qs = need_reviewed_qs
        # 复习了的question
        self.reviewed_qs = reviewed_qs
        # 停止复习的question
        self.paused_qs = paused_qs


class AllNoteHandleResults(Base):
    """所有文件处理之后的结果"""

    def __init__(self):
        self.results = []

    def add(self, result):
        self.results.append(result)

    def accept(self, visitor):
        """访问者模式"""
        return visitor.visit(self)


if __name__ == '__main__':
    print(repr(QA()))
