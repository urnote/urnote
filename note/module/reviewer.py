import datetime

from kit.review_algorithm import ReviewAlgorithm, ReviewInfo


class IReviewRecordDB:
    def all_id(self):
        """get id of all items need to be _REVIEWED

        include  id of  all item whose nt <= today()

        be consider of memory footprint,this should be implement in oncrete db
        or db framework
        """
        raise NotImplementedError

    def need_review(self, id_):
        """judge if the item of this id should be _REVIEWED

        As all_id method, should be implement in concrete db or db framework
        """
        raise NotImplementedError

    def update(self, id_: int, fd: int, ef: float,
               lt: datetime.date, nt: datetime.date):
        raise NotImplementedError

    def query(self, id_) -> (
            int, float, datetime.datetime.date, datetime.datetime.date):
        raise NotImplementedError

    def add(self, fd, ef, lt, nt, id_=None) -> int:
        """
        Returns:
            返回新item的id,如果id_不为空,则直接返回id_
        """
        raise NotImplementedError


class Reviewer:
    def __init__(self, _review_record_db: IReviewRecordDB):
        self.review_algorithm = ReviewAlgorithm()
        self._review_record_db = _review_record_db

    def new(self, id_=None, interval=None, time=None):
        review_info = self.review_algorithm.new(interval=interval,
                                                date_offset=time)

        new_id = self._review_record_db.add(
            review_info.fd, review_info.ef, review_info.lt, review_info.nt,
            id_=id_)

        if id_ is not None:
            assert new_id == id_
        else:
            assert new_id is not None

        return new_id

    def review(self, id_, grade, time=None):
        fd, ef, lt, nt = self._review_record_db.query(id_)
        fd, ef, lt, nt = self.review_algorithm.review(
            ReviewInfo(fd, ef, lt, nt), grade, date_offset=time)
        self._review_record_db.update(id_, fd, ef, lt, nt)

    def need_review(self, id_):
        return self._review_record_db.need_review(id_)
