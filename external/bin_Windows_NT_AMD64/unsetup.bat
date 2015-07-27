@echo off

setlocal

call %~dp0base.bat
call %VIP_BASE_SCRIPT%

call %VIP_INSTALL_DIR%/elevate.bat %~f0 %*
if not %errorLevel% == 3 exit /b

call %~dp0\..\..\daemon.bat all stop

for %%x in (%VIP_SERVICES%) do schtasks /Delete /TN %%x_start_%VIP_DAEMON_POSTFIX% /F
for %%x in (%VIP_SERVICES%) do schtasks /Delete /TN %%x_stop_%VIP_DAEMON_POSTFIX% /F

netsh advfirewall firewall delete rule name="%VIP_FIREWALL_RULE_NAME%"

echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause