"""
显示所有字体颜色效果,选择后用来配置note控制台字体颜色,见stdouthelper模块.
"""
from colorama import init, Style, Fore


def display_all_fore():
    """在控制台展示所有的Fore的style效果"""
    init()
    _display(Fore)


def _display(class_):
    from prettytable import PrettyTable

    x = PrettyTable(["符号", "效果"])
    x.align["符号"] = "l"
    x.padding_width = 1

    for key, value in class_.__dict__.items():
        x.add_row([
            '{}{}'.format(Style.RESET_ALL, key),
            '{flag}{message}'.format(flag=value, message='hello world')
        ])

    print(x)


if __name__ == '__main__':
    display_all_fore()
