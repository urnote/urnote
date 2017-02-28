import datetime
import os
import shutil
import sys
from unittest.mock import patch

from integration.config import BASE_DIR, ExpectedRootDir, ExpectedDbPath
from sqlalchemy import asc

from note import __main__
from note.infrastructure.db import BaseDB, ReviewRecord


class DBTools(BaseDB):
    def add(self, id_, fd, ef, lt, nt):
        record = ReviewRecord(Id=id_, FD=fd, EF=ef, LT=lt, NT=nt)
        self._ses.add(record)
        self._ses.commit()

    @classmethod
    def cmp_db(cls, path1, path2):
        db1 = cls(path=path1)
        db2 = cls(path=path2)
        records1 = db1._ses.query(ReviewRecord).order_by(
            asc(ReviewRecord.Id)).all()
        records2 = db2._ses.query(ReviewRecord).order_by(
            asc(ReviewRecord.Id)).all()
        assert records1 == records2
        return records1 == records2


def init_case1_pre(path):
    db = DBTools(path=path)
    # id,fd,ef,lt,nt
    rows = [
        # 今天是datetime.date(2016, 11, 13)

        # 复习计划中
        (1, 3, 1.7, datetime.date(2016, 11, 10), datetime.date(2099, 12, 31)),
        # 需要今天复习但是没有复习的
        (3, 3, 1.7, datetime.date(2016, 11, 10), datetime.date(2016, 11, 13)),
        # 记得的
        (4, 3, 1.7, datetime.date(2016, 11, 10), datetime.date(2016, 11, 13)),
        # 不记得
        (5, 3, 1.7, datetime.date(2016, 11, 10), datetime.date(2016, 11, 13)),
        # 需要暂停
        (6, 3, 1.7, datetime.date(2016, 11, 10), datetime.date(2016, 11, 13)),
        # 已经暂停的
        (7, 3, 1.7, datetime.date(2016, 11, 10), datetime.date(2016, 11, 12)),
        # 决定解除暂停状态的
        (8, 3, 1.7, datetime.date(2016, 11, 10), datetime.date(2016, 11, 12))
    ]
    for id_, fd, ef, lt, nt in rows:
        db.add(id_=id_, fd=fd, ef=ef, lt=lt, nt=nt)
    db.close()


def init_case1_status(path):
    init_case1_pre(path)


def init_case1_commit(path):
    db = DBTools(path=path)
    # id,fd,ef,lt,nt
    rows = [
        # 今天是datetime.date(2016, 11, 13)

        # 复习计划中
        (1, 3, 1.7, datetime.date(2016, 11, 10), datetime.date(2099, 12, 31)),
        # 需要今天复习但是没有复习的
        (3, 3, 1.7, datetime.date(2016, 11, 10), datetime.date(2016, 11, 13)),
        # 记得的
        (4, 6, 1.8, datetime.date(2016, 11, 13), datetime.date(2016, 11, 19)),
        # 不记得
        (5, 4, 1.3, datetime.date(2016, 11, 13), datetime.date(2016, 11, 14)),
        # 需要暂停
        (6, 3, 1.7, datetime.date(2016, 11, 10), datetime.date(2016, 11, 13)),
        # 已经暂停的
        (7, 3, 1.7, datetime.date(2016, 11, 10), datetime.date(2016, 11, 12)),
        # 决定解除暂停状态的
        (8, 3, 1.7, datetime.date(2016, 11, 10), datetime.date(2016, 11, 12)),
        (9, 3, 1.7, datetime.date(2016, 11, 13), datetime.date(2016, 11, 16))
    ]
    for id_, fd, ef, lt, nt in rows:
        db.add(id_=id_, fd=fd, ef=ef, lt=lt, nt=nt)
    db.close()


CASE1_PRE_PATH = BASE_DIR + ExpectedRootDir('case1', 'pre')
CASE1_STATUS_PATH = BASE_DIR + ExpectedRootDir('case1', 'after_status')
CASE1_COMMIT_PATH = BASE_DIR + ExpectedRootDir('case1', 'after_commit')

CASE1_PRE_DB_PATH = BASE_DIR + ExpectedDbPath('case1', 'pre')
CASE1_STATUS_DB_PATH = BASE_DIR + ExpectedDbPath('case1', 'after_status')
CASE1_COMMIT_DB_PATH = BASE_DIR + ExpectedDbPath('case1', 'after_commit')


def create_test_sample1():
    shutil.rmtree(CASE1_PRE_PATH + '/.NOTE')
    shutil.rmtree(CASE1_PRE_PATH + '/TASK')
    with patch('os.getcwd', return_value=CASE1_PRE_PATH):
        sys.argv = ['note', 'init']
        __main__.run()
    init_case1_pre(CASE1_PRE_DB_PATH)


def create_test_sample2():
    shutil.rmtree(CASE1_STATUS_PATH)
    shutil.copytree(CASE1_PRE_PATH, CASE1_STATUS_PATH)
    with patch('os.getcwd', return_value=CASE1_STATUS_PATH):
        sys.argv = ['note', 'status']
        __main__.run()


def create_test_sample3():
    shutil.rmtree(CASE1_COMMIT_PATH)
    shutil.copytree(CASE1_PRE_PATH, CASE1_COMMIT_PATH)
    with patch('os.getcwd', return_value=CASE1_COMMIT_PATH):
        sys.argv = ['note', 'commit']
        __main__.run()


def create_test_sample():
    create_test_sample1()
    create_test_sample2()
    create_test_sample3()

    # os.remove(CASE1_STATUS_DB_PATH)
    # os.remove(CASE1_COMMIT_DB_PATH)
    # init_case1_status(CASE1_STATUS_DB_PATH)
    # init_case1_commit(CASE1_COMMIT_DB_PATH)


def init_db():
    if os.path.exists(CASE1_PRE_DB_PATH):
        os.remove(CASE1_PRE_DB_PATH)
    if os.path.exists(CASE1_STATUS_DB_PATH):
        os.remove(CASE1_STATUS_DB_PATH)
    if os.path.exists(CASE1_COMMIT_DB_PATH):
        os.remove(CASE1_COMMIT_DB_PATH)
    init_case1_pre(CASE1_PRE_DB_PATH)
    init_case1_status(CASE1_STATUS_DB_PATH)
    init_case1_commit(CASE1_COMMIT_DB_PATH)


if __name__ == '__main__':
    print('begin')
    # create_test_sample()
    # 需要单独执行是因为create时,没有释放数据库连接.
    init_db()
    print('end')
