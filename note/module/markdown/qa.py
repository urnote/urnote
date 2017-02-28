from note.module.element import QA


class MarkdownQA(QA):
    def __str__(self):
        return self.question.lstrip('# \t\r\f\v　')


if __name__ == '__main__':
    mqa = MarkdownQA()
    mqa.question = "#123"
    assert str(mqa) == '123'
