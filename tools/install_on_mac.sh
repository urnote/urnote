#!/usr/bin/env bash

brew install coreutils

chmod +x note_for_mac.sh
path=$(grealpath note_for_mac.sh)
ln -s ${path} /usr/local/bin/note