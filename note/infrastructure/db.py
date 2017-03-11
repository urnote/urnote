import datetime

from sqlalchemy import Column, Integer, Date, Float
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from note.module.reviewer import IReviewRecordDB

_Base = declarative_base()


def _init(path=None):
    eng = create_engine(path)

    _Base.metadata.bind = eng
    _Base.metadata.create_all()

    return eng, sessionmaker(bind=eng)


class ReviewRecord(_Base):
    __tablename__ = "ReviewRecord"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    FD = Column(Integer)
    EF = Column(Float)
    LT = Column(Date)
    NT = Column(Date)

    def __eq__(self, other):
        return all((self.Id == other.Id,
                    self.FD == other.FD,
                    self.EF == other.EF,
                    self.LT == other.LT,
                    self.NT == other.NT))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str(self.__dict__)


class BaseDB:
    def __init__(self, path):
        assert path is not None
        path = 'sqlite:///{path}'.format(path=path)
        self._eng, _Class = _init(path)
        self._ses = _Class()

    def close(self):
        self._ses.close()


class DB(BaseDB, IReviewRecordDB):
    def query(self, id_) -> (
            int, float, datetime.datetime.date, datetime.datetime.date):
        # Use first() function instead of one().
        # It will return None if there is no results.
        review_record = self._ses.query(ReviewRecord).filter(
            ReviewRecord.Id == id_).first()

        assert review_record is not None
        assert isinstance(review_record, ReviewRecord)

        return (review_record.FD, review_record.EF, review_record.LT,
                review_record.NT)

    def add(self, fd, ef, lt, nt, id_=None):
        if id_ is not None:
            record = ReviewRecord(Id=id_, FD=fd, EF=ef, LT=lt, NT=nt)
            self._ses.add(record)
        else:
            record = ReviewRecord(FD=fd, EF=ef, LT=lt, NT=nt)
            self._ses.add(record)
            self._ses.flush()

        self._ses.commit()
        return record.Id

    def need_review(self, id_):
        rs = self._ses.query(ReviewRecord).filter(
            ReviewRecord.Id == id_,
            ReviewRecord.NT <= datetime.datetime.today())
        return True if rs.count() == 1 else False

    def update(self, id_: int, fd: int, ef: float,
               lt: datetime.date, nt: datetime.date):
        self._ses.query(ReviewRecord).filter(ReviewRecord.Id == id_).update(
            {
                ReviewRecord.FD: fd,
                ReviewRecord.EF: ef,
                ReviewRecord.LT: lt,
                ReviewRecord.NT: nt
            })
        self._ses.commit()

    def all_id(self):
        rs = self._ses.query(ReviewRecord).filter(
            ReviewRecord.NT <= datetime.datetime.today())
        return tuple(book.Id for book in rs)
