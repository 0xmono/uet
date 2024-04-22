#!/bin/sh

BASEDIR=$(dirname "$0")
#echo "$BASEDIR"
#echo "$PWD"

#Build Unreal Engine project script
python3 "$BASEDIR/uet/build.py" "$PWD" "$@"
