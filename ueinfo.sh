#!/bin/sh

BASEDIR=$(dirname "$0")
#echo "$BASEDIR"
#echo "$PWD"

#Info about Unreal Engine installations in system
python3 "$BASEDIR/uet/info.py" "$PWD" "$@"
