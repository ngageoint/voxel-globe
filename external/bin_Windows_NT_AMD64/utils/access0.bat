@echo off

setlocal

call %~dp0..\base.bat
call %VIP_BASE_SCRIPT%

call %VIP_INSTALL_DIR%/elevate.bat %~f0 %*
if not %errorLevel% == 0 exit /b

sc create access0 type= interact type= own binpath= %VIP_PROJECT_ROOT:/=\%\wrap.bat 
sc config access0 type= interact type= own binpath= %VIP_PROJECT_ROOT:/=\%\wrap.bat 

sc start ui0detect
sc start access0

endlocal