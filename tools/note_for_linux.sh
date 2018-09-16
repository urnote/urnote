#!/usr/bin/env bash

SCRIPT_PATH=$(readlink -f "$0")
ROOT_PATH=$(dirname $(dirname "${SCRIPT_PATH}"))
export PYTHONPATH=${PYTHONPATH}:${ROOT_PATH}
python3 -m note "$@"