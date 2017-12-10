import re

# 所有正则都不匹配的表示普通问题

# 新加入的笔记:以问好结尾或者以问好加数字结尾
NEW = re.compile("""
^
(?P<question>.*?)
[\s\u200b]*?
[\?？]
[\s\u200b]*?
(?P<cmd_string>[\d]*?)
[\s\u200b]*?
$
""", re.VERBOSE)
NEW_TITLE = '{question}    ?  {cmd_string}'.format

# 没到复习时间的笔记
OLD = re.compile("""
^
(?P<question>.*?)
[\s\u200b]*?
\[(?::question:|❓)\]
\(
(?:SOH)?(?P<id>\d{,7})(?:EOT)?
\)
[\s\u200b]*
$
""", re.VERBOSE)
OLD_TITLE = "{question}    [❓]({id:d})  \u200b".format

# 需要复习的
NEED_REVIEWED = re.compile("""
^
(?P<question>.*?)
[\s\u200b]*?
\[(?::notification:|🔔)\]
\(
(?:SOH)?(?P<id>\d{,7})(?:EOT)?
\)
[\s\u200b]*
(?P<cmd_string>.*?)
[\s\u200b]*
$
""", re.VERBOSE)
NEED_REVIEWED_TITLE = (
    "{question}    [🔔]({id:d})  \u200b{cmd_string}".format)

# 停止复习的笔记的标题
PAUSED = re.compile("""
^
(?P<question>.*?)
[\s\u200b]*?
\[(?::closed_book:|📕)\]
\(
(?:SOH)?(?P<id>\d{,7})(?:EOT)?
\)
[\s\u200b]*
(?P<cmd_string>.*?)
[\s\u200b]*
$
""", re.VERBOSE)
PAUSED_TITLE = (
    "{question}    [📕]({id:d})  \u200b{cmd_string}".format)
