import unittest

from note.module.markdown.title_pat import *


class MyTestCase(unittest.TestCase):
    def test_new_note(self):
        # 一定是非空字符串
        mo = NEW.match("")
        self.assertIsNone(mo)
        # 最后一个非空字符表示必须含有非空字符
        mo = NEW.match(" ")
        self.assertIsNone(mo)
        # 最后一个是问号满足,不是问号不满足
        mo = NEW.match("?")
        self.assertEqual(mo.groupdict(), {'question': '', 'cmd_string': ''})
        mo = NEW.match("?  1")
        self.assertEqual(mo.groupdict(), {'question': '', 'cmd_string': '1'})
        mo = NEW.match("? \u200b 1 \u200b ")
        self.assertEqual(mo.groupdict(), {'question': '', 'cmd_string': '1'})
        mo = NEW.match("?          \u200b  \u200b")
        self.assertEqual(mo.groupdict(), {'question': '', 'cmd_string': ''})
        mo = NEW.match("def ?: question ? 1")
        self.assertEqual(mo.groupdict(),
                         {'question': 'def ?: question', 'cmd_string': '1'})
        mo = NEW.match("def ?: question ?")
        self.assertEqual(mo.groupdict(),
                         {'question': 'def ?: question', 'cmd_string': ''})

        mo = NEW.match("x")
        self.assertIsNone(mo)

    def test_old_note(self):
        """去掉后面的空白部分后,剩下的是[:question:](SOH1234567EOT)类型表示旧笔记"""

        invalids = [
            ("", "空字符串"),
            ("[:question:](SOH1234567ET)", "后面的被破坏了"),
            ("[:question:](SOH1234567EOT) x", "后面还有其他部分")
        ]
        for string, msg in invalids:
            self.assertIsNone(OLD.match(string),
                              '{} {}不应该满足'.format(string, msg))

        mo = OLD.match("[:question:](SOH1234567EOT) \u200b")
        self.assertEqual(mo.groupdict(), {'question': '', 'id': '1234567'})
        mo = OLD.match("[:question:](SOH1234567EOT)  ")
        self.assertEqual(mo.groupdict(), {'question': '', 'id': '1234567'})

    def test_need_reviewed_note(self):
        invalids = [
            ("", "空字符串"),
            ("[:notification:](SOH1234567ET) ", "后面的被破坏了"),
        ]
        for string, msg in invalids:
            self.assertIsNone(NEED_REVIEWED.match(string),
                              '{} {}不应该满足'.format(string, msg))

        # 没有评分的
        mo = NEED_REVIEWED.match(
            "# question [:notification:](SOH1234567EOT) \u200b")
        self.assertEqual(mo.groupdict(),
                         {'question': '# question', 'id': '1234567',
                          'cmd_string': ''})
        mo = NEED_REVIEWED.match("# question [:notification:](SOH1234567EOT) ")
        self.assertEqual(mo.groupdict(),
                         {'question': '# question', 'id': '1234567',
                          'cmd_string': ''})
        # 有评分的
        mo = NEED_REVIEWED.match(
            "# question [:notification:](SOH1234567EOT)  \u200bV\u200b")
        self.assertEqual(mo.groupdict(),
                         {'question': '# question', 'id': '1234567',
                          'cmd_string': 'V'})
        mo = NEED_REVIEWED.match(
            "# question [:notification:](SOH1234567EOT)  X C")
        self.assertEqual(mo.groupdict(),
                         {'question': '# question', 'id': '1234567',
                          'cmd_string': 'X C'})

    def test_paused_note(self):
        invalids = [
            ("", "空字符串"),
            ("# question [:closed_book:](SOH1234567EOT", "后面的被破坏了"),
        ]
        for string, msg in invalids:
            self.assertIsNone(PAUSED.match(string),
                              '{} {}不应该满足'.format(string, msg))

        # 没有评分的
        mo = PAUSED.match("# question [:closed_book:](SOH1234567EOT)")
        self.assertEqual(mo.groupdict(),
                         {'question': '# question', 'id': '1234567',
                          'cmd_string': ''})
        mo = PAUSED.match(
            "# question [:closed_book:](SOH1234567EOT)  \u200b\u200b\u200b")
        self.assertEqual(mo.groupdict(),
                         {'question': '# question', 'id': '1234567',
                          'cmd_string': ''})
        mo = PAUSED.match(
            "## 通用视图修改context ?:方式    [:closed_book:](SOH0000042EOT)	\u200b"
        )
        self.assertEqual(mo.groupdict(),
                         {'question': '## 通用视图修改context ?:方式', 'id': '0000042',
                          'cmd_string': ''})
        mo = PAUSED.match(
            "## 通用视图修改context ?:方式    [:closed_book:](SOH0000042EOT)	​")
        self.assertEqual(mo.groupdict(),
                         {'question': '## 通用视图修改context ?:方式', 'id': '0000042',
                          'cmd_string': ''})
        # 有评分的
        mo = PAUSED.match("# question [:closed_book:](SOH1234567EOT) C")
        self.assertEqual(mo.groupdict(),
                         {'question': '# question', 'id': '1234567',
                          'cmd_string': 'C'})
        mo = PAUSED.match("# question [:closed_book:](SOH1234567EOT)  C ")
        self.assertEqual(mo.groupdict(),
                         {'question': '# question', 'id': '1234567',
                          'cmd_string': 'C'})
        mo = PAUSED.match("# question [:closed_book:](SOH1234567EOT)  C xx")
        self.assertEqual(mo.groupdict(),
                         {'question': '# question', 'id': '1234567',
                          'cmd_string': 'C xx'})


if __name__ == '__main__':
    unittest.main()
