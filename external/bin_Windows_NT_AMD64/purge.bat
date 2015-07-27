@echo off

setlocal

call %~dp0base.bat
call %VIP_BASE_SCRIPT%

call %VIP_INSTALL_DIR%/elevate.bat %~f0 %*
if not %errorLevel% == 0 exit /b

echo Are you ABSOLUTELY SURE you want to remove the ENTIRE DATABASE cluster, ALL data in it, all injested data, all installed services, and programs associated with this project?

set /p confirm="Confirm by typing YeS: " %=%

if "%confirm%" NEQ "YeS" goto canceled

call %VIP_INSTALL_DIR%\unsetup.bat

rmdir /Q /S %VIP_INSTALL_DIR:/=\%\Apache24 %VIP_INSTALL_DIR:/=\%\erlang 
rmdir /Q /S %VIP_INSTALL_DIR:/=\%\osgeo4w %VIP_INSTALL_DIR:/=\%\postgresql 
rmdir /Q /S %VIP_INSTALL_DIR:/=\%\python %VIP_INSTALL_DIR:/=\%\rabbitmq_server
rmdir /Q /S %VIP_INSTALL_DIR:/=\%\vips %VIP_INSTALL_DIR:/=\%\visualsfm
rmdir /Q /S %VIP_LOG_DIR:/=\% %VIP_POSTGRESQL_DATABASE:/=\% 
for /D %%i in (%VIP_DATABASE_DIR:/=\%\rabbit*) do rmdir /Q /S %%i
for /D %%i in (%VIP_DJANGO_STATIC_ROOT:/=\%\*) do rmdir /Q /S %%i
for /D %%i in (%VIP_DJANGO_MEDIA_ROOT:/=\%\*) do rmdir /Q /S %%i
del /Q %VIP_RABBITMQ_BASE_DRIVE%%VIP_RABBITMQ_BASE_PATH%.erlang.cookie %VIP_BASE_SCRIPT:/=\% 

echo It is done

goto done

:canceled
echo Purge aborted. Good choice.

:done

echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause

endlocal