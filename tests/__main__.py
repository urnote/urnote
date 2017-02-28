"""
运行所有单元测试和集成测试
"""
import os
import sys
import unittest

TEST_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# 项目根目录
ROOT_DIR = os.path.dirname(TEST_ROOT_DIR)

sys.path.insert(0, TEST_ROOT_DIR)
sys.path.insert(0, ROOT_DIR)


def unit_test_suite():
    loader = unittest.TestLoader()
    suite = loader.discover('unit')
    return suite


def integration_test_suite():
    """测试简单情况，模拟view，替换了getcwd，使其返回虚拟空间路径"""
    loader = unittest.TestLoader()
    suite = loader.discover("integration")
    return suite


def all_suites():
    return unittest.TestSuite([unit_test_suite(), integration_test_suite()])


if __name__ == '__main__':
    from note.infrastructure import config

    assert config.DEBUG is True
    unittest.main(defaultTest='all_suites', verbosity=1)
