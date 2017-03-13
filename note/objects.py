import argparse
import gettext

from note.controller import Controller
from note.infrastructure import config
from note.infrastructure.db import DB
from note.infrastructure.error import CMDError
from note.infrastructure.logging import LoggerFactory
from note.module.app import Initializer, Runner, Purger
from note.module.argparser import CustomArgumentParser
from note.module.filehandler import WorkspaceManager
from note.module.markdown.filehandler import MarkdownFileContentHandler
from note.module.pathhelper import PathHelper
from note.module.qahandler.purgeqahandler import PurgeQAHandler
from note.module.qahandler.reviewqahandler import ReviewQAHandler
from note.module.reviewer import Reviewer
from note.module.visitor import StatusResultVisitor, CommitResultVisitor
from note.view import View


def get_logger():
    workspace_manger = get_workspace_manager()
    if config.DEBUG:
        return LoggerFactory.create_debug_logger(config.APP_NAME)
    else:
        # 如果还没有工作空间,创建一个stream_logger,并且在init之后应该更改为
        # file_logger;如果有工作空间,直接创建file_logger
        if workspace_manger.have_workspace():
            return LoggerFactory.create_prod_logger(
                config.APP_NAME, workspace_manger.path_helper.log_path)
        else:
            return LoggerFactory.create_prod_logger_stream(config.APP_NAME)


def get_path_helper():
    return PathHelper()


def get_content_handler(path, relpath):
    return MarkdownFileContentHandler(path, relpath)


def get_parser(view):
    translation = gettext.translation('argparse', config.LOCALES, ('zh_CN',))
    argparse._ = translation.gettext

    parser = CustomArgumentParser(description='', prog="", view=view)
    parser.add_argument('--doc', help='帮助文档', action='store_true')
    parser.add_argument(
        '-v', '--version', help='查看版本号', action='store_true')

    sp = parser.add_subparsers(help='子命令', dest='cmd')

    sp.add_parser('init', help="在当前目录创建工作空间")
    sp.add_parser('status', help="显示工作空间状态信息")

    commit_parser = sp.add_parser('commit', help="提交")
    commit_parser.add_argument(
        '-t', '--time',
        help='模拟本次提交为time天前提交', nargs='?', type=int)

    purger = sp.add_parser(
        'purge', help='指定一个目录,将其中所有章节还原为普通章节')
    purger.add_argument(
        'path', help='需要处理的目录,可以使用相对路径和绝对路径')

    return parser


def get_workspace_manager():
    return WorkspaceManager(path_helper=get_path_helper())


def get_initializer():
    initializer = Initializer(get_workspace_manager())
    return initializer


_db = None


def get_runner():
    global _db
    try:
        _db = DB(get_path_helper().db_path)
    except FileNotFoundError:
        raise CMDError.uninitialized()
    r = Reviewer(_review_record_db=_db)
    title_handler = ReviewQAHandler(reviewer=r)
    runner = Runner(
        qa_handler=title_handler,
        workspace_manger=get_workspace_manager(),
        get_content_handler=get_content_handler
    )
    return runner


def get_purger():
    p = PurgeQAHandler()
    purger = Purger(
        p, workspace_manger=get_workspace_manager(),
        get_content_handler=get_content_handler
    )
    return purger


def get_status_result_visitor():
    return StatusResultVisitor()


def get_commit_result_visitor():
    return CommitResultVisitor()


def get_controller():
    view = View()
    controller = Controller(
        view=view, logger=get_logger(), parser=get_parser(view),
        get_purger=get_purger, get_runner=get_runner,
        get_initializer=get_initializer,
        get_status_result_visitor=get_status_result_visitor,
        get_commit_result_visitor=get_commit_result_visitor
    )
    return controller


def release():
    if _db:
        _db.close()


if __name__ == '__main__':
    assert get_content_handler(__file__, None) == \
           MarkdownFileContentHandler(__file__, None)
