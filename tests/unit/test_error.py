import unittest

from note.infrastructure.error import (
    FileContentError, ArgParserError, CMDError)


class MyTestCase(unittest.TestCase):
    err = None

    def assertMessageEqual(self, description, solution):
        self.assertEqual(self.err.exception.message, (description, solution))

    def test_file_content_error(self):
        with self.assertRaises(FileContentError) as self.err:
            raise FileContentError.wrong_encoding('hello.md')
        self.assertMessageEqual(
            '文件"hello.md"无法打开',
            '使用UTF-8编码的文件,或者修改"./NOTE/ignore.default"文件忽略'
        )

    def test_arg_parser_error(self):
        with self.assertRaises(ArgParserError) as self.err:
            raise ArgParserError('***')
        self.assertMessageEqual('***', '输入"note --help"查看帮助信息')

    def test_cmd_error(self):
        with self.assertRaises(CMDError) as self.err:
            raise CMDError.duple_init(root_dir='ROOT_DIR')
        self.assertMessageEqual(
            '无法使用命令"init"创建重复或嵌套的工作空间,已存在工作空间:ROOT_DIR',
            ''
        )

        with self.assertRaises(CMDError) as self.err:
            raise CMDError.uninitialized()
        self.assertMessageEqual(
            '未找到工作空间', '使用命令"note init"创建工作空间'
        )

        with self.assertRaises(CMDError) as self.err:
            raise CMDError.purge_exist_but_not_empty()
        self.assertMessageEqual('PURGE目录已存在且不为空', '手动清空PURGE目录')

        with self.assertRaises(CMDError) as self.err:
            raise CMDError.file_not_in_current_workspace()
        self.assertMessageEqual('目标路径不在工作空间中', '')


if __name__ == '__main__':
    unittest.main()
