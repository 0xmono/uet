#!/bin/sh

BASEDIR=$(dirname "$0")
#echo "$BASEDIR"
#echo "$PWD"

#Inspect Unreal Engine project/build script
python3 "$BASEDIR/uet/view_logs.py" "$PWD" "$@"
