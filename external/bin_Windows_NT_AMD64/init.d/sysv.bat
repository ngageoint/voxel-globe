@echo off
setlocal
call %~dp0..\base.bat
call %VIP_BASE_SCRIPT%
%VIP_PYTHON_DIR%/python %*
REM Since this is called by a batch/python hybrid, end now!
exit /b 
endlocal