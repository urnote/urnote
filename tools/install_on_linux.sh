#!/usr/bin/env bash

chmod +x note_for_linux.sh
path=$(realpath note_for_linux.sh)
ln -s ${path} /usr/local/bin/note