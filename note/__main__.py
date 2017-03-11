from note.controller import Controller
from note.infrastructure.error import CMDError
from note.objects import (
    get_parser, get_initializer, get_runner, get_purger, get_path_helper,
    get_logger, release)
from note.view import RunResultView


def run(args=None):
    CMDError.get_path_helper = get_path_helper

    view = RunResultView()
    controller = Controller(
        view=view, logger=get_logger(), parser=get_parser(view),
        get_purger=get_purger, get_runner=get_runner,
        get_initializer=get_initializer
    )

    controller.run(args)
    release()


if __name__ == '__main__':
    run()
