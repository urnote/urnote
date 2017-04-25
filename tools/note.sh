#!/usr/bin/env bash

# 用于启动note，只用于DEBUG模式

SCRIPT_PATH=$(readlink -f "$0")
ROOT_PATH=$(dirname $(dirname "${SCRIPT_PATH}"))
export PYTHONPATH=${PYTHONPATH}:${ROOT_PATH}

echo "DEBUG MODE"
echo "NOTE MODULE SEARCH PATH: ${ROOT_PATH}"
echo "------------------------------------"

trap "echo '发生错误,检查config.DEBUG是否设置为TRUE'" ERR

python3 -m note "$@"