#!/bin/sh

BASEDIR=$(dirname "$0")
#echo "$BASEDIR"
#echo "$PWD"

#Get status of Unreal Engine project/build script
python3 "$BASEDIR/uet/status.py" "$PWD" "$@"
