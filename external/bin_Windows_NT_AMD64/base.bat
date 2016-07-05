@echo off

REM Base directories, necessary for knowing how to load the other files.
REM In the future, you'll be able to CHANGE VIP_INSTALL_DIR here... maybe

REM Get canonical path of ../../
if not defined VIP_PROJECT_DIR for %%i in (%~dp0/../..) do set VIP_PROJECT_DIR__TEMP=%%~fi
if not defined VIP_PROJECT_DIR set VIP_PROJECT_DIR=%VIP_PROJECT_DIR__TEMP:\=/%
set VIP_PROJECT_DIR__TEMP=

if not defined VIP_BASE_SCRIPT set VIP_BASE_SCRIPT=%VIP_PROJECT_DIR%/vip.bat
