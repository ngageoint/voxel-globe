@echo off

call %~dp0/daemon.bat all start

echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause
