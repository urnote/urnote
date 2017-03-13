from note.module.element import AllNoteHandleResults, OneNoteHandleResult
from note.utils import Base


class Visitor:
    def visit(self, results: AllNoteHandleResults):
        raise NotImplementedError


class StatusResultVisitor(Visitor):
    def visit(self, results: AllNoteHandleResults):
        """返回HandleResults的汇总信息,该信息将用于视图输出"""
        report = ReportAfterStatus()
        for result in results.results:
            assert isinstance(result, OneNoteHandleResult)
            if len(result.new_qs):
                lq = LocatedQuestions(result.location, result.new_qs)
                report.new_qs_report.append(lq)
            if len(result.reviewed_qs):
                lq = LocatedQuestions(result.location, result.reviewed_qs)
                report.reviewed_qs_report.append(lq)
            if len(result.paused_qs):
                lq = LocatedQuestions(result.location, result.paused_qs)
                report.paused_qs_report.append(lq)
            report.need_reviewed_num += len(result.need_reviewed_qs)
        return report


class ReportAfterStatus(Base):
    """表示Visitor访问AllNoteHandleResults之后生成的报告,此信息将由视图展示"""

    def __init__(self):
        # 新添加的笔记
        self.new_qs_report = []
        # 复习了的笔记
        self.reviewed_qs_report = []
        # 暂停了的笔记
        self.paused_qs_report = []
        # 需要复习的笔记数量
        self.need_reviewed_num = 0


class LocatedQuestions(Base):
    """表示一组处于相同位置的问题"""

    def __init__(self, location, qs):
        self.location = location
        self.qs = qs


class CommitResultVisitor(Visitor):
    def visit(self, results: AllNoteHandleResults):
        """返回HandleResults的汇总信息,该信息将用于视图输出"""
        report = ReportAfterCommit()
        for result in results.results:
            assert isinstance(result, OneNoteHandleResult)
            report.new_num += len(result.new_qs)
            report.reviewed_num += len(result.reviewed_qs)
            report.paused_num += len(result.paused_qs)
            report.need_reviewed_num += len(result.need_reviewed_qs)
        return report


class ReportAfterCommit(Base):
    def __init__(self):
        # 新添加的笔记数量
        self.new_num = 0
        # 复习了的笔记数量
        self.reviewed_num = 0
        # 暂停了的笔记数量
        self.paused_num = 0
        # 需要复习的笔记数量
        self.need_reviewed_num = 0
