@echo off

call %~dp0/daemon.bat all stop

echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause
