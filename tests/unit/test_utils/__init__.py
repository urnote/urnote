import unittest

from note.utils import truncate_for_display


class TestUtils(unittest.TestCase):
    def test_truncate_for_display(self):
        s = '12345'
        self.assertEqual(truncate_for_display(s, 5), '12345')
        s = '123456'
        self.assertEqual(truncate_for_display(s, 5), '12...')
        s = '1234'
        self.assertEqual(truncate_for_display(s, 5), '1234')
        s = '1234\n'
        self.assertEqual(truncate_for_display(s, 5), '1234\n')
        s = '1234\n\n'
        self.assertEqual(truncate_for_display(s, 5), '12...')
        s = '\x0112345\x01'
        self.assertEqual(truncate_for_display(s, 5), '\x0112345\x01')
        s = '一二三'
        self.assertEqual(truncate_for_display(s, 5), '一...')
        s = '1一二三'
        self.assertEqual(truncate_for_display(s, 5), '1...')
        s = '\x01一二三'
        self.assertEqual(truncate_for_display(s, 5), '\x01一...')

        s = '12345\n'
        self.assertEqual(truncate_for_display(s, 5, True), '12345\n')
        s = '123456\n'
        self.assertEqual(truncate_for_display(s, 5, True), '12...\n')
        s = '1234\n'
        self.assertEqual(truncate_for_display(s, 5, True), '1234\n')
        s = '1234\n\n'
        self.assertEqual(truncate_for_display(s, 5, True), '1234\n\n')
        s = '1234\n\n\n'
        self.assertEqual(truncate_for_display(s, 5, True), '12...\n')
        s = '\x0112345\x01\n'
        self.assertEqual(truncate_for_display(s, 5, True), '\x0112345\x01\n')
        s = '一二三\n'
        self.assertEqual(truncate_for_display(s, 5, True), '一...\n')
        s = '1一二三\n'
        self.assertEqual(truncate_for_display(s, 5, True), '1...\n')
        s = '\x01一二三\n'
        self.assertEqual(truncate_for_display(s, 5, True), '\x01一...\n')


if __name__ == '__main__':
    unittest.main()
