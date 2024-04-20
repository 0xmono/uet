@echo off

rem Build Unreal Engine project script
python %~dp0\uet\build.py %cd% %*
