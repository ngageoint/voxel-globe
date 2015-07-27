@echo off

setlocal

call %~dp0base.bat
call %VIP_BASE_SCRIPT%

call %VIP_INSTALL_DIR%/elevate.bat %~f0 %*
if not %errorLevel% == 0 exit /b

REM echo Breaking inheritance at %VIP_PROJECT_ROOT%
REM No need for this
REM icacls %VIP_PROJECT_ROOT% /inheritance:d 

echo Enabling inheritance under %VIP_PROJECT_ROOT%. (This will take a while)
icacls %VIP_PROJECT_ROOT:/=\%\* /T /inheritance:e > %VIP_LOG_DIR%/prepare_install.log

echo Giving %VIP_DAEMON_USER% read and execute access to %VIP_PROJECT_ROOT%

icacls %VIP_PROJECT_ROOT% /grant:r "%VIP_DAEMON_USER%":(OI)(CI)(RX)
REM icacls %VIP_PROJECT_ROOT% /T /inheritance:d /grant:r "%VIP_DAEMON_USER%":(OI)(RX)
REM One day this may be needed too... *sigh*
REM icacls %VIP_INSTALL_DIR% /T /inheritance:d /grant:r "%VIP_DAEMON_USER%":(OI)(RX)

echo Giving %VIP_DAEMON_USER% Read/Write/Execute Permissions to %VIP_LOG_DIR% and %VIP_DATABASE_DIR%

icacls %VIP_DATABASE_DIR% /grant:r "%VIP_DAEMON_USER%":(OI)(CI)(M)
icacls %VIP_LOG_DIR% /grant:r "%VIP_DAEMON_USER%":(OI)(CI)(M)

echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause

endlocal