import operator
from enum import Enum


class Base:
    """
    参考：
        http://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes
        http://stackoverflow.com/questions/4522617/equality-of-python-classes-using-slots?noredirect=1&lq=1
    """

    def __eq__(self, other):
        """
        比较的时候：
            两个对象都是普通对象，且类型相同
            两个对象都是有slot的对象，类型相同
            两个对象都有slot和__dict__,类型相同

        对于slot的比较，只比较self本身的__slot__中存在的属性，不比较继承的部分

        参考:
            http://stackoverflow.com/questions/472000/usage-of-slots
        """
        if isinstance(other, self.__class__):
            slot_equal = True
            if hasattr(self, "__slots__"):
                attr_getters = [
                    operator.attrgetter(attr) for attr in self.__slots__]
                slot_equal = all(
                    getter(self) == getter(other) for getter in attr_getters)
            dict_equal = self.__dict__ == other.__dict__
            return slot_equal and dict_equal
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        """如果要实现集合，字典键等地方的相等性判断需要实现该方法"""


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
            assert value in (Command.YES, Command.NO, Command.PAUSE)
        if self.state == QAState.PAUSED:
            assert value == Command.CONTINUE

        self._command = value

    def __str__(self):
        """该方法决定了对象的显示字符串,根据情况应该重载"""
        return self.question

    def __repr__(self):
        tmp = {}
        for attr in self.__slots__:
            tmp[attr] = getattr(self, attr)
        for key, value in self.__dict__:
            tmp[key] = value
        return str(tmp)


class QAState(Enum):
    NORMAL = 0  # 未加入的(用户给的) 用户可以将其转换为NEW状态
    OLD = 2  # 已经加入了的,程序会保持OLD或者转为NEED_REVIEWED
    NEED_REVIEWED = 3  # 已加入的,需要复习  ...
    PAUSED = 5  # 已加入的,暂停复习


class Command(Enum):
    ADD = 0
    YES = 1
    NO = 2
    PAUSE = 3
    CONTINUE = 4


class StateTransition(Enum):
    """用户关心的程序执行过程中的状态转换
    没有发生转移使用None表示,如OLD_TO_OLD
    """
    NEW_TO_OLD = 0  # 新加入的
    NEED_REVIEWED_TO_OLD = 1  # 复习了的(不是暂停)
    NEED_REVIEWED_TO_PAUSED_OLD = 2  # 暂停了的

    # 需要复习的包括两种类型
    TO_NEED_REVIEWED = 3  # 本次新加入的需要复习的
    STILL_NEED_REVIEWED = 4  # 表示没有改变，还是需要复习


class QuestionGroup(Base):
    def __init__(self, relative_path, questions):
        self.relative_path = relative_path
        self.questions = questions

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__


class RunResult(Base):
    """程序run之后的结果"""

    def __init__(self):
        # 需要复习的单词的数量
        self.need_reviewed_num = 0
        # 停止复习的数量
        self.paused_num = 0

        # 每个文件中新的question
        # eg: [QuestionGroup]
        self.new_qs_each_file = []
        self.new_num = 0

        # 每个文件中复习了的question
        # eg: [QuestionGroup]
        self.reviewed_qs_each_file = []
        self.reviewed_num = 0

    def add_reviewed_qs(self, reviewed_qs: QuestionGroup):
        num = len(reviewed_qs.questions)
        if num:
            self.reviewed_qs_each_file.append(reviewed_qs)
            self.reviewed_num += num

    def add_new_qs(self, new_qs: QuestionGroup):
        num = len(new_qs.questions)
        if num:
            self.new_qs_each_file.append(new_qs)
            self.new_num += num
