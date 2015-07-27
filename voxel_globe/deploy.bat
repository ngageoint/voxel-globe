:; `dirname "$0"`/_deploy.bsh "${@}"; exit $?
@echo off

%~dp0start_manage.bat collectstatic --noinput

echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause
