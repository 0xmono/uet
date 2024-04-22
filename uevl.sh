#!/bin/sh

BASEDIR=$(dirname "$0")
#echo "$BASEDIR"
#echo "$PWD"

#View logs for Unreal Engine script
python3 "$BASEDIR/uet/view_logs.py" "$PWD" "$@"
