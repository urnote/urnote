#!/usr/bin/env bash

# 方式一
#   ./install_for_debug.sh /usr/bin/note_debug
#   之后可在shell中使用note_debug命令,如 note_debug --help
# 方式二
#   ./install_for_debug.sh /home/workspace
#   之后进入/home/workspace，使用./note.sh即可,如 ./note.sh --help

chmod +x note.sh

if [ $# -eq 0 ]
then
    echo "未设置链接文件路径参数"
    exit 0
elif [ $# -ne 1 ]
then
    echo "参数个数错误"
    exit 0
fi

path=$(realpath note.sh)
ln -s ${path} $1