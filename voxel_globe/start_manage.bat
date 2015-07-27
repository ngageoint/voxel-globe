:; `dirname "$0"`/_start_manage.bsh "${@}"; exit $?
@echo off
%~dp0..\wrap.bat python %~dp0manage.py %*