import copy
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
        self.mock_reviewer = Mock(spec=Reviewer)
        # noinspection PyTypeChecker
        self.handler = ReviewQAHandler(self.mock_reviewer)

    def tearDown(self):
        self.mock_reviewer.reset_mock()
        Singleton.clear()

    def test_normal(self):
        qa = QA("# chapter", "内容", None, QAState.NORMAL, None, None)
        self._check(qa)

    def test_normal_with_command(self):
        qa = QA("# chapter", "内容", None, QAState.NORMAL, Command.ADD, None)
        self._check(qa, expected_transition=StateTransition.NEW_TO_OLD)
        self.assertFalse(self.mock_reviewer.new.called)

    def test_normal_with_interval(self):
        qa = QA("# chapter", "内容", None, QAState.NORMAL, Command.ADD, 10)
        self._check(qa, expected_transition=StateTransition.NEW_TO_OLD)
        self.assertFalse(self.mock_reviewer.new.called)

    def test_old(self):
        """还没到复习时间"""
        qa = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        self.mock_reviewer.need_review.return_value = False
        self._check(qa)
        self.mock_reviewer.need_review.assert_called_once_with(1)

    def test_old2(self):
        """到复习时间"""
        qa = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        expected_qa = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None,
                         None)
        self.mock_reviewer.need_review.return_value = True
        self._check(qa,
                    expected_qa=expected_qa,
                    expected_transition=StateTransition.OLD_TO_NEED_REVIEWED,
                    expected_modified=True)
        self.mock_reviewer.need_review.assert_called_once_with(1)

    def test_need_reviewed(self):
        qa = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None, None)
        self._check(qa, expected_transition=StateTransition.STILL_NEED_REVIEWED)

    def test_need_reviewed_with_V(self):
        qa = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.REMEMBER,
                None)
        self._check(qa,
                    expected_transition=StateTransition.NEED_REVIEWED_TO_OLD)
        self.assertFalse(self.mock_reviewer.review.called)

    def test_need_reviewed_with_X(self):
        qa = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.FORGET,
                None)
        self._check(qa,
                    expected_transition=StateTransition.NEED_REVIEWED_TO_OLD)
        self.assertFalse(self.mock_reviewer.review.called)

    def test_need_reviewed_with_P(self):
        qa = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.PAUSE,
                None)
        self._check(
            qa,
            expected_transition=StateTransition.NEED_REVIEWED_TO_PAUSED_OLD
        )

    def test_paused(self):
        qa = QA("# chapter", "内容", 1, QAState.PAUSED, None, None)
        self._check(qa)

    def test_paused_with_C(self):
        qa = QA("# chapter", "内容", 1, QAState.PAUSED, Command.CONTINUE, None)
        self._check(qa,
                    expected_transition=StateTransition.PAUSED_TO_NEED_REVIEWED)

    def _check(self, qa, expected_qa=None, expected_transition=None,
               expected_modified=False):
        if not expected_qa:
            expected_qa = copy.deepcopy(qa)

        transition, modified = self.handler.handle(qa, commit=False, time=None)

        self.assertEqual(
            (transition, modified),
            (expected_transition, expected_modified)
        )
        self.assertEqual(qa, expected_qa)


class TestReviewQAHandler_Commit(unittest.TestCase):
    """测试QAHandler正确处理QA"""

    def setUp(self):
        self.mock_reviewer = Mock(spec=Reviewer)
        # noinspection PyTypeChecker
        self.handler = ReviewQAHandler(self.mock_reviewer)

    def tearDown(self):
        self.mock_reviewer.reset_mock()
        Singleton.clear()

    def test_normal(self):
        qa = QA("# chapter", "内容", None, QAState.NORMAL, None, None)
        expected = QA("# chapter", "内容", None, QAState.NORMAL, None, None)
        self._check(expected, qa)

    def test_normal_with_command(self):
        qa = QA("# chapter", "内容", None, QAState.NORMAL, Command.ADD, None)
        self.mock_reviewer.new.return_value = 1
        expected = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        transition = StateTransition.NEW_TO_OLD
        self._check(qa, expected, transition)
        self.mock_reviewer.new.assert_called_once_with(interval=None, time=None)

    def test_normal_with_interval(self):
        qa = QA("# chapter", "内容", None, QAState.NORMAL, Command.ADD, 10)
        self.mock_reviewer.new.return_value = 1
        expected = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        transition = StateTransition.NEW_TO_OLD
        self._check(qa, expected, transition)
        self.mock_reviewer.new.assert_called_once_with(interval=10, time=None)

    def test_old(self):
        """还没到复习时间"""
        qa = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        self.mock_reviewer.need_review.return_value = False
        expected = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        self._check(qa, expected)
        self.mock_reviewer.need_review.assert_called_once_with(1)

    def test_old2(self):
        """到复习时间"""
        qa = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        self.mock_reviewer.need_review.return_value = True
        expected = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None, None)
        transition = StateTransition.OLD_TO_NEED_REVIEWED
        self._check(qa, expected, transition)
        self.mock_reviewer.need_review.assert_called_once_with(1)

    def test_need_reviewed(self):
        qa = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None, None)
        expected = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None, None)
        transition = StateTransition.STILL_NEED_REVIEWED
        self._check(qa, expected, transition)

    def test_need_reviewed_with_V(self):
        qa = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.REMEMBER,
                None)
        expected = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        transition = StateTransition.NEED_REVIEWED_TO_OLD
        self._check(qa, expected, transition)
        self.mock_reviewer.review.assert_called_once_with(1, Grade.EASY,
                                                          time=None)

    def test_need_reviewed_with_X(self):
        qa = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.FORGET,
                None)
        expected = QA("# chapter", "内容", 1, QAState.OLD, None, None)
        transition = StateTransition.NEED_REVIEWED_TO_OLD
        self._check(qa, expected, transition)
        self.mock_reviewer.review.assert_called_once_with(1, Grade.FORGOTTEN,
                                                          time=None)

    def test_need_reviewed_with_P(self):
        qa = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, Command.PAUSE,
                None)
        expected = QA("# chapter", "内容", 1, QAState.PAUSED, None, None)
        transition = StateTransition.NEED_REVIEWED_TO_PAUSED_OLD
        self._check(qa, expected, transition)
        self.assertFalse(self.mock_reviewer.review.called)

    def test_paused(self):
        qa = QA("# chapter", "内容", 1, QAState.PAUSED, None, None)
        expected = QA("# chapter", "内容", 1, QAState.PAUSED, None, None)
        self._check(qa, expected)

    def test_paused_with_C(self):
        qa = QA("# chapter", "内容", 1, QAState.PAUSED, Command.CONTINUE, None)
        expected = QA("# chapter", "内容", 1, QAState.NEED_REVIEWED, None, None)
        self._check(qa, expected, StateTransition.PAUSED_TO_NEED_REVIEWED)

    def _check(self, qa, expected_qa, expected_transition=None):
        raw_qa = copy.deepcopy(qa)
        transition, modified = self.handler.handle(qa, commit=True, time=None)
        self.assertEqual(
            (transition, modified),
            (expected_transition, raw_qa != expected_qa)
        )
        self.assertEqual(qa, expected_qa)


if __name__ == '__main__':
    unittest.main()
