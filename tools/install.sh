#!/usr/bin/env bash

# 用于向/usr/bin中添加note命令

SCRIPT_PATH=$(readlink -f "$0")
DIR_PATH=$(dirname "${SCRIPT_PATH}")
EXE_PATH="${DIR_PATH}/note"
ln -s ${EXE_PATH} /usr/bin/note