#!/bin/sh
# Called by launchd with absolute tmux path and the selected session name.
set -eu
"$1" has-session -t "=$2" 2>/dev/null || \
    "$1" new-session -d -s "$2" || "$1" has-session -t "=$2"
