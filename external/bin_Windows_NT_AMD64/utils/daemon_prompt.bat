@echo off

REM Create a command prompt as the VIP DAEMON USER, usually WINDOWS NT/NETWORK 
REM SERVICE. Need psexec for this special user, else it is impossible.

setlocal

call %~dp0..\base.bat
call %VIP_BASE_SCRIPT%

call %VIP_INSTALL_DIR%/elevate.bat %~f0 %*
if %errorLevel% == 1 exit /b

echo %~dp0psexec -i -u "%VIP_DAEMON_USER%" %VIP_PROJECT_ROOT%/wrap.bat
%~dp0psexec -i -u "%VIP_DAEMON_USER%" %VIP_PROJECT_ROOT%/wrap.bat

endlocal