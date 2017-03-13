import unittest
from unittest.mock import Mock

from note.module.element import QA, Command, QAState, StateTransition
from note.module.qahandler.reviewqahandler import ReviewQAHandler
from note.module.reviewer import Reviewer
from note.utils.pattern import Singleton
from note.utils.review_algorithm import Grade


class TestReviewQAHandler_Status(unittest.TestCase):
    """测试QAHandler正确处理QA"""

    def setUp(self):
        self.mock_view = Mock(spec=Reviewer)
        # noinspection PyTypeChecker
        self.handler = ReviewQAHandler(self.mock_view)

    def tearDown(self):
        self.mock_view.reset_mock()
        Singleton.clear()

    def test_normal(self):
        qas = QA("# chapter", "内容", None, QAState.NORMAL, None, None)
        expected = QA("# chapter", "内容", None, QAState.NORMAL, None, None)
        self._check(expected, qas)

    def test_normal_with_command(self):
        qas = QA("# chapter", "内容", None, QAState.NORMAL, Command.ADD, None)
        expected = QA("# chapter", "内容", None, QAState.NORMAL, Command.ADD,
                      None)
        transition = StateTransition.NEW_TO_OLD
        self._check(qas, expected, transition)
        self.assertFalse(self.mock_view.new.called)

    def test_normal_with_interval(self):
        qas = QA("# chapter", "内容", None, QAState.NORMAL, Command.ADD, 10)
        expected = QA("# chapter", "内容", None, QAState.NORMAL, Command.ADD, 10)
        transition = StateTransition.NEW_TO_OLD
        self._check(qas, expected, transition)
        self.assertFalse(self.mock_view.new.called)

    def test_old(self):
        """还没到复习时间"""
        qas = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        self.mock_view.need_review.return_value = False
        expected = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        self._check(qas, expected)
        self.mock_view.need_review.assert_called_once_with(1)

    def test_old2(self):
        """到复习时间"""
        qas = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        self.mock_view.need_review.return_value = True
        expected = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None, None)
        transition = StateTransition.OLD_TO_NEED_REVIEWED
        self._check(qas, expected, transition)
        self.mock_view.need_review.assert_called_once_with(1)

    def test_need_reviewed(self):
        qas = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None, None)
        expected = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None, None)
        transition = StateTransition.STILL_NEED_REVIEWED
        self._check(qas, expected, transition)

    def test_need_reviewed_with_V(self):
        qas = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.REMEMBER, None)
        expected = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.REMEMBER,
                      None)
        transition = StateTransition.NEED_REVIEWED_TO_OLD
        self._check(qas, expected, transition)
        self.assertFalse(self.mock_view.review.called)

    def test_need_reviewed_with_X(self):
        qas = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.FORGET, None)
        expected = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.FORGET,
                      None)
        transition = StateTransition.NEED_REVIEWED_TO_OLD
        self._check(qas, expected, transition)
        self.assertFalse(self.mock_view.review.called)

    def test_need_reviewed_with_P(self):
        qas = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.PAUSE,
                 None)
        expected = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED,
                      Command.PAUSE, None)
        transition = StateTransition.NEED_REVIEWED_TO_PAUSED_OLD
        self._check(qas, expected, transition)

    def test_paused(self):
        qas = QA("# chapter", "内容", 1, QAState.PAUSED, None, None)
        expected = QA("# chapter", "内容", 1, QAState.PAUSED, None, None)
        self._check(qas, expected)

    def test_paused_with_C(self):
        """加入后发现还没到复习时间"""
        qas = QA("# chapter", "内容", 1, QAState.PAUSED, Command.CONTINUE, None)
        self.mock_view.need_review.return_value = False
        expected = QA("# chapter", "内容", 1, QAState.PAUSED, Command.CONTINUE,
                      None)
        self._check(qas, expected)
        self.mock_view.need_review.assert_called_once_with(1)

    def test_paused_with_C2(self):
        """加入后发现到复习时间"""
        qas = QA("# chapter", "内容", 1, QAState.PAUSED, Command.CONTINUE, None)
        self.mock_view.need_review.return_value = True
        expected = QA("# chapter", "内容", 1, QAState.PAUSED, Command.CONTINUE,
                      None)
        transition = StateTransition.OLD_TO_NEED_REVIEWED
        self._check(qas, expected, transition)
        self.mock_view.need_review.assert_called_once_with(1)

    def _check(self, qa, expected, transition=None):
        self.assertEqual(self.handler.handle(qa, commit=False, time=None),
                         transition)
        self.assertEqual(qa, expected)


class TestReviewQAHandler_Commit(unittest.TestCase):
    """测试QAHandler正确处理QA"""

    def setUp(self):
        self.mock_view = Mock(spec=Reviewer)
        # noinspection PyTypeChecker
        self.handler = ReviewQAHandler(self.mock_view)

    def tearDown(self):
        self.mock_view.reset_mock()
        Singleton.clear()

    def test_normal(self):
        qas = QA("# chapter", "内容", None, QAState.NORMAL, None, None)
        expected = QA("# chapter", "内容", None, QAState.NORMAL, None, None)
        self._check(expected, qas)

    def test_normal_with_command(self):
        qas = QA("# chapter", "内容", None, QAState.NORMAL, Command.ADD, None)
        self.mock_view.new.return_value = 1
        expected = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        transition = StateTransition.NEW_TO_OLD
        self._check(qas, expected, transition)
        self.mock_view.new.assert_called_once_with(interval=None, time=None)

    def test_normal_with_interval(self):
        qas = QA("# chapter", "内容", None, QAState.NORMAL, Command.ADD, 10)
        self.mock_view.new.return_value = 1
        expected = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        transition = StateTransition.NEW_TO_OLD
        self._check(qas, expected, transition)
        self.mock_view.new.assert_called_once_with(interval=10, time=None)

    def test_old(self):
        """还没到复习时间"""
        qas = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        self.mock_view.need_review.return_value = False
        expected = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        self._check(qas, expected)
        self.mock_view.need_review.assert_called_once_with(1)

    def test_old2(self):
        """到复习时间"""
        qas = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        self.mock_view.need_review.return_value = True
        expected = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None, None)
        transition = StateTransition.OLD_TO_NEED_REVIEWED
        self._check(qas, expected, transition)
        self.mock_view.need_review.assert_called_once_with(1)

    def test_need_reviewed(self):
        qas = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None, None)
        expected = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None, None)
        transition = StateTransition.STILL_NEED_REVIEWED
        self._check(qas, expected, transition)

    def test_need_reviewed_with_V(self):
        qas = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.REMEMBER, None)
        expected = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        transition = StateTransition.NEED_REVIEWED_TO_OLD
        self._check(qas, expected, transition)
        self.mock_view.review.assert_called_once_with(1, Grade.EASY, time=None)

    def test_need_reviewed_with_X(self):
        qas = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.FORGET, None)
        expected = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        transition = StateTransition.NEED_REVIEWED_TO_OLD
        self._check(qas, expected, transition)
        self.mock_view.review.assert_called_once_with(1, Grade.FORGOTTEN,
                                                      time=None)

    def test_need_reviewed_with_P(self):
        qas = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.PAUSE,
                 None)
        expected = QA("# chapter", "内容", 1, QAState.PAUSED, None, None)
        transition = StateTransition.NEED_REVIEWED_TO_PAUSED_OLD
        self._check(qas, expected, transition)
        self.assertFalse(self.mock_view.review.called)

    def test_paused(self):
        qas = QA("# chapter", "内容", 1, QAState.PAUSED, None, None)
        expected = QA("# chapter", "内容", 1, QAState.PAUSED, None, None)
        self._check(qas, expected)

    def test_paused_with_C(self):
        """加入后发现还没到复习时间"""
        qas = QA("# chapter", "内容", 1, QAState.PAUSED, Command.CONTINUE, None)
        self.mock_view.need_review.return_value = False
        expected = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        self._check(qas, expected)
        self.mock_view.need_review.assert_called_once_with(1)

    def test_paused_with_C2(self):
        """加入后发现到复习时间"""
        qas = QA("# chapter", "内容", 1, QAState.PAUSED, Command.CONTINUE, None)
        self.mock_view.need_review.return_value = True
        expected = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None, None)
        transition = StateTransition.OLD_TO_NEED_REVIEWED
        self._check(qas, expected, transition)
        self.mock_view.need_review.assert_called_once_with(1)

    def _check(self, qa, expected, transition=None):
        self.assertEqual(self.handler.handle(qa, commit=True, time=None),
                         transition)
        self.assertEqual(qa, expected)


if __name__ == '__main__':
    unittest.main()
