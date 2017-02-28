"""
提供两种logger,一个用于开发,一个用于真实环境
"""

import logging
import traceback

# 在日志文件中记录用户使用时发生的ERROR的详细信息
_PROD_LOG_FORMAT_ERROR_FILE = (
    '%(asctime)s\n' +
    '-' * 80 + '\n' +
    '%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n' +
    '%(message)s\n' +
    '-' * 80 + '\n'
)


class LoggerFactory:
    @staticmethod
    def create_debug_logger(app_name):
        """
        debug的logger,只是将prod时输出到文件的展示在标准界面
        """
        stream_handler = logging.StreamHandler()
        return LoggerFactory._assemble_logger(app_name, stream_handler)

    @staticmethod
    def create_prod_logger(app_name, log_file):
        """
        将程序预测为不可能发生的AppError以及未预测到的异常记录到日志中等级均为
        critical,如果还没有初始化工作空间,返回的是null_logger
        """
        prod_file_handler = logging.FileHandler(log_file, encoding='utf-8')
        return LoggerFactory._assemble_logger(app_name, prod_file_handler)

    @classmethod
    def create_prod_logger_stream(cls, app_name):
        logger = logging.getLogger(app_name)
        logger.addHandler(logging.StreamHandler())
        return logger

    @staticmethod
    def _assemble_logger(app_name, handler):
        class ModifyInfo(logging.Filter):
            """
            调整回溯堆栈的位置,默认情况下在显示完message之后显示
            """

            def filter(self, record: logging.LogRecord):
                # record.exc_info 是元组,默认情况下,处理过程中判断是否有exc_info,
                # 有的话会在消息末尾添加回溯堆栈
                traceback_text = ''.join(
                    traceback.format_exception(*record.exc_info))
                traceback_text = traceback_text.strip()
                record.msg += traceback_text
                record.exc_info = ''
                return True

        handler.setLevel(logging.CRITICAL)
        handler.setFormatter(logging.Formatter(_PROD_LOG_FORMAT_ERROR_FILE))

        logger = logging.getLogger(app_name)
        logger.setLevel(logging.CRITICAL)

        # 必须先将其设置为空
        logger.handlers = []
        logger.addHandler(handler)
        logger.addFilter(ModifyInfo())

        return logger
