@echo off

rem Get status of Unreal Engine project/build script
python %~dp0\uet\status.py %cd% %*
