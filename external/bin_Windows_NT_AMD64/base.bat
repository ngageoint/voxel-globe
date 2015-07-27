@echo off

REM Base directories, necessary for knowing how to load the other files.
REM In the future, you'll be able to CHANGE VIP_INSTALL_DIR here... maybe

REM Get canonical path of ../../
if not defined VIP_PROJECT_ROOT for %%i in (%~dp0/../..) do set VIP_PROJECT_ROOT__TEMP=%%~fi
if not defined VIP_PROJECT_ROOT set VIP_PROJECT_ROOT=%VIP_PROJECT_ROOT__TEMP:\=/%
set VIP_PROJECT_ROOT__TEMP

if not defined VIP_BASE_SCRIPT set VIP_BASE_SCRIPT=%VIP_PROJECT_ROOT%/vip.bat
