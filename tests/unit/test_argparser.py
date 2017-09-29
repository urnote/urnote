import unittest
from argparse import Namespace
from unittest.mock import Mock

from note.objects import get_parser
from note.view import View


class TestArgParser(unittest.TestCase):
    def setUp(self):
        self.mock_view = Mock(spec=View)
        self.parser = get_parser(self.mock_view)

    def tearDown(self):
        self.mock_view.reset_mock()

    def _parse(self, args):
        return self.parser.parse_args(args.split())

    def test_all(self):
        input_and_expected = [
            (
                'purge E:/hello',
                Namespace(cmd='purge', path='E:/hello', doc=False,
                          version=False)
            ),
            (
                'commit -t 3',
                Namespace(cmd='commit', time=3, doc=False, version=False, not_link=False,
                          short=False)
            ),
            (
                'commit -t ',
                Namespace(cmd='commit', time=None, doc=False, version=False, not_link=False,
                          short=False)
            )
        ]
        for item in input_and_expected:
            self.assertEqual(self._parse(item[0]), item[1])


if __name__ == '__main__':
    unittest.main()
