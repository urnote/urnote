import os
import unittest

from note.module.element import QA, Command, QAState
from note.module.markdown.filehandler import MarkdownFileContentHandler


class TestMarkdownFileHandler(unittest.TestCase):
    PATH = 'test_file_handler'

    @classmethod
    def setUpClass(cls):
        open(cls.PATH, 'w').close()

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.PATH)


class TestMarkdownFileHandler_Get_Qas(TestMarkdownFileHandler):
    def test_normal(self):
        content = "# chapter\n" \
                  "内容"
        expected = [QA("# chapter", "内容", None, None, QAState.NORMAL, None, None)]
        self._check(content, expected)

    def test_normal2(self):
        content = "# chapter\n" \
                  "内容\n" \
                  "# chapter\n" \
                  "内容"
        expected = [QA("# chapter", "内容", None, None, QAState.NORMAL, None, None),
                    QA("# chapter", "内容", None, None, QAState.NORMAL, None, None)]
        self._check(content, expected)

    def test_normal3(self):
        content = "# chapter\n" \
                  "ANSWER\n" \
                  "---\n" \
                  "BODY"
        expected = [
            QA("# chapter", "ANSWER", "BODY", None, QAState.NORMAL, None, None)]
        self._check(content, expected)

    def test_normal4(self):
        content = "# chapter\n" \
                  "ANSWER\n" \
                  "---\n" \
                  "BODY\n" \
                  "## chapter\n" \
                  "ANSWER"
        expected = [
            QA("# chapter", "ANSWER", "BODY", None, QAState.NORMAL, None, None),
            QA("## chapter", "ANSWER", None, None, QAState.NORMAL, None, None), ]
        self._check(content, expected)

    def test_normal_with_command(self):
        content = "# chapter ?\n" \
                  "内容"
        expected = [
            QA("# chapter", "内容", None, None, QAState.NORMAL, Command.ADD, None)]
        self._check(content, expected)

    def test_normal_with_interval(self):
        content = "# chapter ? 10\n" \
                  "内容"
        expected = [
            QA("# chapter", "内容", None, None, QAState.NORMAL, Command.ADD, 10)]
        self._check(content, expected)

    def test_old(self):
        content = "# chapter    [:question:](SOH0000001EOT)\n" \
                  "内容"
        expected = [QA("# chapter", "内容", None, 1, QAState.OLD, None, None)]
        self._check(content, expected)

    def test_need_reviewed(self):
        content = "# chapter    [:notification:](SOH0000001EOT)\n" \
                  "内容"
        expected = [QA("# chapter", "内容", None, 1, QAState.NEED_REVIEWED, None, None)]
        self._check(content, expected)

    def test_need_reviewed_with_V(self):
        content = "# chapter    [:notification:](SOH0000001EOT)  V\n" \
                  "内容"
        expected = [
            QA("# chapter", "内容", None, 1, QAState.NEED_REVIEWED, Command.REMEMBER, None)]
        self._check(content, expected)

    def test_need_reviewed_with_X(self):
        content = "# chapter    [:notification:](SOH0000001EOT)  X\n" \
                  "内容"
        expected = [
            QA("# chapter", "内容", None, 1, QAState.NEED_REVIEWED, Command.FORGET, None)]
        self._check(content, expected)

    def test_need_reviewed_with_P(self):
        content = "# chapter    [:notification:](SOH0000001EOT)  P\n" \
                  "内容"
        expected = [
            QA("# chapter", "内容", None, 1, QAState.NEED_REVIEWED, Command.PAUSE,
               None)]
        self._check(content, expected)

    def test_paused(self):
        content = "# chapter    [:closed_book:](SOH0000001EOT)\n" \
                  "内容"
        expected = [QA("# chapter", "内容", None, 1, QAState.PAUSED, None, None)]
        self._check(content, expected)

    def test_paused_with_C(self):
        content = "# chapter    [:closed_book:](SOH0000001EOT) C\n" \
                  "内容"
        expected = [
            QA("# chapter", "内容", None, 1, QAState.PAUSED, Command.CONTINUE, None)]
        self._check(content, expected)

    def _check(self, content, expected):
        qas = self._get_qas(content)
        self.assertEqual(list(qas), expected)

    def _write(self, content):
        with open(self.PATH, 'w', encoding='utf-8') as fo:
            fo.write(content)

    def _get_qas(self, content):
        self._write(content)
        handler = MarkdownFileContentHandler(self.PATH, None)
        qas = handler.get_qas()
        return qas


class TestMarkdownFileHandler_Save_Qas(TestMarkdownFileHandler):
    def test_normal(self):
        qas = [QA("# chapter", "内容",None, None, QAState.NORMAL, None, None)]
        expected = "# chapter\n" \
                   "内容"
        self._check(expected, qas)

    def test_normal2(self):
        qas = [QA("# chapter", "内容", None, None, QAState.NORMAL, None, None),
               QA("# chapter", "内容", None, None, QAState.NORMAL, None, None)]
        expected = "# chapter\n" \
                   "内容\n" \
                   "# chapter\n" \
                   "内容"
        self._check(expected, qas)

    def test_normal3(self):
        qas = [
            QA("# chapter", "ANSWER", "BODY", None, QAState.NORMAL, None, None)]
        expected = "# chapter\n" \
                   "ANSWER\n" \
                   "---\n" \
                   "BODY"
        self._check(expected, qas)

    def test_normal4(self):
        qas = [
            QA("# chapter", "ANSWER", "BODY", None, QAState.NORMAL, None, None),
            QA("## chapter", "ANSWER", None, None, QAState.NORMAL, None, None), ]
        expected = "# chapter\n" \
                   "ANSWER\n" \
                   "---\n" \
                   "BODY\n" \
                   "## chapter\n" \
                   "ANSWER"
        self._check(expected, qas)

    def test_normal_with_command(self):
        qas = [QA("# chapter", "内容", None, None, QAState.NORMAL, Command.ADD, None)]
        expected = "# chapter    ?  \n" \
                   "内容"
        self._check(expected, qas)

    def test_normal_with_interval(self):
        qas = [QA("# chapter", "内容", None, None, QAState.NORMAL, Command.ADD, 10)]
        expected = "# chapter    ?  10\n" \
                   "内容"
        self._check(expected, qas)

    def test_old(self):
        qas = [QA("# chapter", "内容", None, 1, QAState.OLD, None, None)]
        expected = "# chapter    [:question:](SOH0000001EOT)  \u200b\n" \
                   "内容"
        self._check(expected, qas)

    def test_need_reviewed(self):
        qas = [QA("# chapter", "内容", None, 1, QAState.NEED_REVIEWED, None, None)]
        expected = "# chapter    [:notification:](SOH0000001EOT)  \u200b\n" \
                   "内容"
        self._check(expected, qas)

    def test_need_reviewed_with_V(self):
        qas = [
            QA("# chapter", "内容", None, 1, QAState.NEED_REVIEWED, Command.REMEMBER, None)]
        expected = "# chapter    [:notification:](SOH0000001EOT)  \u200bV\n" \
                   "内容"
        self._check(expected, qas)

    def test_need_reviewed_with_X(self):
        qas = [
            QA("# chapter", "内容", None, 1, QAState.NEED_REVIEWED, Command.FORGET, None)]
        expected = "# chapter    [:notification:](SOH0000001EOT)  \u200bX\n" \
                   "内容"
        self._check(expected, qas)

    def test_need_reviewed_with_P(self):
        qas = [QA("# chapter", "内容", None, 1, QAState.NEED_REVIEWED, Command.PAUSE,
                  None)]
        expected = "# chapter    [:notification:](SOH0000001EOT)  \u200bP\n" \
                   "内容"
        self._check(expected, qas)

    def test_paused(self):
        qas = [QA("# chapter", "内容",None, 1, QAState.PAUSED, None, None)]
        expected = "# chapter    [:closed_book:](SOH0000001EOT)  \u200b\n" \
                   "内容"
        self._check(expected, qas)

    def test_paused_with_C(self):
        qas = [QA("# chapter", "内容", None, 1, QAState.PAUSED, Command.CONTINUE, None)]
        expected = "# chapter    [:closed_book:](SOH0000001EOT)  \u200bC\n" \
                   "内容"
        self._check(expected, qas)

    def _save_qas(self, qas):
        handler = MarkdownFileContentHandler(self.PATH, None)
        handler.save_qas(qas)

    def _check(self, expected, qas):
        self._save_qas(qas)
        content = self._read()
        self.assertEqual(content, expected)

    def _read(self):
        with open(self.PATH, 'r', encoding='utf-8')as fo:
            return fo.read()


if __name__ == '__main__':
    unittest.main()
