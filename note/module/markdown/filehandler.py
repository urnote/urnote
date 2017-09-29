from note.infrastructure.error import FileContentError
from note.module.element import QAState, QA, Command
from note.module.filehandler import FileContentHandler
from note.module.markdown.qa import MarkdownQA
from note.module.markdown.title_pat import *
from note.utils.os import fs


class MarkdownFileContentHandler(FileContentHandler):
    def __init__(self, path, relpath):
        self._path = path
        self._relpath = relpath
        with open(path, "r", encoding="utf-8") as fo:
            try:
                self._raw_file_content = fo.read()
            except:
                raise FileContentError.wrong_encoding(self._relpath)
        self._toc = self._get_toc_part(self._raw_file_content)

    @staticmethod
    def _get_toc_part(file_content):
        """拿到第一个标题之前的所有内容

        对于没有标题的文件,所有的内容均视为头
        """
        # 匹配第一个标题之前的东西
        pat = re.compile(r".*?^[ \t\r\f\v]*(?=#)", re.DOTALL | re.MULTILINE)
        match_obj = pat.match(file_content)

        return match_obj.group(0) if match_obj is not None else file_content

    def get_qas(self):
        """拿到从self.path指向的文件解析出的QA"""
        text_qas = self._get_text_qas()
        return (self._create_qa(header, body) for header, body in text_qas)

    def _get_text_qas(self):
        """将markdown文件以#为标志拆为head和body,以供进一步解析"""
        content = self._escape()
        items = self._split(content)
        for item in items:
            tmp = item.groupdict()
            header = tmp["header"]
            body = tmp["body"]
            body = self._unescape(body)
            yield header, body

    def _escape(self):
        """
        由于使用markdown中的标题识别QA,但是在正则匹配的过程中,符合标题的字符串
        可能会出现在代码块中,如:

        ```python
        import this
        # 这个不是标题,是注释
        ```

        为了防止将代码块中的#识别为标题语法,该方法将转义所有的代码块中的#,如上面的
        代码块将被转义为:

        ```python
        import this
        \# 这个不是标题,是注释
        ```

        Returns:
            转义之后的文本
        """
        # 匹配代码块
        pat = re.compile(
            r"""
            [ \t\r\f\v]*```
            .*?
            [ \t\r\f\v]*```
            $
            """,
            re.VERBOSE | re.DOTALL | re.MULTILINE)
        content = pat.sub(self._sub_inner__headed_sharp, self._raw_file_content)
        return content

    @staticmethod
    def _sub_inner__headed_sharp(match_obj):
        """
        将以#开头的行的#转变为\#,因为是在``` ```中捕获的,所以整个字符串一定是
        以 \n非\n空白* 结束的,开头一般是以python\n开头,至少都会有个\n
        """
        pat = re.compile(
            r"""
            (?<=\n)
            ([ \t\r\f\v]*)
            (\#)(.*?\n)
            """,
            re.VERBOSE)
        return pat.sub(r"\1\#\3", match_obj.group(0))

    @staticmethod
    def _split(content):
        """分割文本为QA片段"""
        pat = re.compile(
            r"""
                ^
                # 表示出了\n之外的多个空白,因为之后还原时需要用到,所以捕获
                # .标题之后需要有一个空白
                (?P<header>[ \t\r\f\v]*
                \#{1,6} # 表示标题#需要转转义
                 .*?)(?:\n|\Z)  # 可以是任何东西,但是不能是\n或者EOF(.*?)$不可以
                (?P<body>.*?)   # 这里是正文,
                # 任何东西,但是只能匹配到下一个标题前,注意这里要避免匹配\#
                (?:(?=\n^[ \t\r\f\v]*\#{1,6})|\Z)
            """,
            re.VERBOSE | re.MULTILINE | re.DOTALL)
        # items是text中所有的东西,按照标题分了组的
        items = pat.finditer(content)
        return items

    @staticmethod
    def _unescape(content: str) -> str:
        pat = re.compile(r"""
        ^
        ([ \t\r\f\v]*)
        (\\\#)
        (.*?\n)
        """, re.VERBOSE | re.MULTILINE)
        return pat.sub(r"\1#\3", content)

    def _create_qa(self, header, body):
        qa = MarkdownQA()
        self._set_attr_from_body(qa, body)
        self._set_attr_from_header(qa, header)
        return qa

    def _set_attr_from_body(self, qa, body):
        qa.body = body
        qa.answer = self._get_answer(body)

    @staticmethod
    def _get_answer(body):
        return body.split('---', 1)[0].strip()

    def _set_attr_from_header(self, qa, header):
        """设置question,state,id,command"""
        pat__type = [
            (NEW, QAState.NORMAL),
            (OLD, QAState.OLD),
            (NEED_REVIEWED, QAState.NEED_REVIEWED),
            (PAUSED, QAState.PAUSED),
        ]
        for pat, state in pat__type:
            mo = pat.match(header)
            if mo:
                group_dict = mo.groupdict()
                qa.question = group_dict['question']
                qa.state = state
                if pat in (OLD, NEED_REVIEWED, PAUSED):
                    qa.id = int(group_dict['id'])
                if pat == NEW:
                    interval = group_dict['cmd_string']
                    # 分数可以是空字符串,表示没有初始间隔
                    if interval == '':
                        qa.command = Command.ADD
                        return
                    try:
                        interval_ = int(interval)
                        # TODO:应该在配置文件中设置最大值.
                        if interval_ > 15:
                            raise ValueError
                    except ValueError:
                        raise FileContentError.wrong_command(
                            location=self._relpath,
                            question=qa.question,
                            grade=interval)
                    qa.command = Command.ADD
                    qa.arg = interval_
                if pat == NEED_REVIEWED:
                    grade = group_dict['cmd_string']
                    if grade:
                        try:
                            grade = self._map_review_command(grade)
                        except FileContentError as err:
                            err.question = qa.question
                            raise err
                        qa.command = grade
                if pat == PAUSED:
                    cmd_string = group_dict['cmd_string']
                    # 必须坚持空,因为['' in '123']为true
                    if cmd_string:
                        if cmd_string in 'CcＣｃ':
                            qa.command = Command.CONTINUE
                        else:
                            raise FileContentError.wrong_command(
                                location=self._relpath,
                                question=qa.question, grade=cmd_string)
                return
        else:
            qa.question = header
            qa.state = QAState.NORMAL

    def _map_review_command(self, command):
        if command in 'XxＸｘ':
            command = Command.FORGET
        elif command in 'VvＶｖ':
            command = Command.REMEMBER
        elif command in 'PpＰｐ':
            command = Command.PAUSE
        else:
            raise FileContentError.wrong_command(
                location=self._relpath, grade=command)
        return command

    def save_qas(self, qas, path=None):
        new_content = self._convert_to_text(qas)
        if path is None:
            with open(self._path, "w", encoding="utf-8") as fo:
                fo.write(new_content)
        else:
            fs.make_dir_of_file(path)
            with open(path, "w", encoding="utf-8") as fo:
                fo.write(new_content)

    def _convert_to_text(self, qas):
        if self._toc:
            new_content = [self._toc]
        else:
            new_content = []
        for qa in qas:
            header, body = self._to_text(qa)
            new_content.append(header)
            new_content.append(body)
        new_content = "\n".join(new_content)
        return new_content

    @staticmethod
    def _to_text(qa: QA):
        assert qa.state is not None
        if qa.state == QAState.NORMAL:
            if qa.command is None:
                return qa.question, qa.body
            if qa.arg is None:
                return NEW_TITLE(question=qa.question, cmd_string=''), qa.body
            return NEW_TITLE(question=qa.question, cmd_string=qa.arg), qa.body
        if qa.state == QAState.OLD:
            return OLD_TITLE(question=qa.question, id=qa.id, ), qa.body
        if qa.state == QAState.NEED_REVIEWED:
            if qa.command:
                command = {
                    Command.REMEMBER: 'V',
                    Command.FORGET: 'X',
                    Command.PAUSE: 'P',
                }[qa.command]
                return NEED_REVIEWED_TITLE(
                    question=qa.question, id=qa.id, cmd_string=command
                ), qa.body
            return NEED_REVIEWED_TITLE(
                question=qa.question, id=qa.id, cmd_string=''
            ), qa.body
        if qa.state == QAState.PAUSED:
            if qa.command:
                return PAUSED_TITLE(
                    question=qa.question, id=qa.id, cmd_string='C'
                ), qa.body
            return PAUSED_TITLE(
                question=qa.question, id=qa.id, cmd_string=''
            ), qa.body

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
