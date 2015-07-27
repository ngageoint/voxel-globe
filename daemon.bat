:; `dirname "$0"`/_daemon.bsh "${@}"; exit $?
@echo off

setlocal enabledelayedexpansion

call %~dp0vip.bat

set VIP_NARG=0
for %%x in (%*) do Set /A VIP_NARG+=1

if not "%VIP_NARG%"=="2" (
  echo ERROR: Two arguments only
  goto usage
)

set ELEVATE=%VIP_INSTALL_DIR%/elevate.bat

REM killall needs admin rights
if /i "killall"=="%2" (
  call %ELEVATE% %~f0 %*
  if "!errorlevel!" == "1" exit /b
)

::Special case all
if /i "%1" == "all" (
  if /i "%2" == "stop" set VIP_RESERVE_ORDER=1
  if /i "%2" == "restart" set VIP_RESERVE_ORDER=1
  if "!VIP_RESERVE_ORDER!" == "1" (
  REM Stop in reverse order, and NO, GOOGLE DID NOT HELP HERE! This is ALL AEN!
	set TEMPTASKS=%VIP_SERVICES%

    set NUMT=0
    for %%x in (!TEMPTASKS!) do set /A NUMT+=1

    for /L %%x in (!NUMT!, -1, 1) do (
      set COUNTT=0
      for %%y in (!TEMPTASKS!) do (
        set /A COUNTT+=1
	    if "!COUNTT!"=="%%x" set TASKS=!TASKS! %%y
      )
    )
    set VIP_RESERVE_ORDER=
  ) else (
    set TASKS=%VIP_SERVICES%
  )
  goto valid_service_name
)
::See if any of the names match
for %%i in (%VIP_SERVICES%) do (
  if /i "%1" == "%%i" (
    set TASKS=%1
    goto valid_service_name
  )
)
goto usage

:valid_service_name
set NEXT=usage
for %%i in (start stop restart status test killall) do (
  if /i "%%i"=="%2" set NEXT=%2
)

if "%NEXT%"=="usage" goto usage
::Skip elevate because there is no reason

REM Create log directories in case they don't exist.
if not exist %VIP_POSTGRESQL_LOG_DIR:/=\% mkdir %VIP_POSTGRESQL_LOG_DIR:/=\%
if not exist %VIP_RABBITMQ_LOG_DIR:/=\% mkdir %VIP_RABBITMQ_LOG_DIR:/=\%
if not exist %VIP_CELERY_LOG_DIR:/=\% mkdir %VIP_CELERY_LOG_DIR:/=\%
if not exist %VIP_NOTEBOOK_LOG_DIR:/=\% mkdir %VIP_NOTEBOOK_LOG_DIR:/=\%
if not exist %VIP_HTTPD_LOG_DIR:/=\% mkdir %VIP_HTTPD_LOG_DIR:/=\%

goto %NEXT%
goto usage
::Just in case something went REALLY wrong?!

:start
for %%t in (%TASKS%) do (
  schtasks /run /TN %%t_start_%VIP_DAEMON_POSTFIX% > nul
  
  call %VIP_INIT_DIR%/%%t waitstart %VIP_DAEMON_TIMEOUT%
  if "!errorlevel!" NEQ "0" (
    python -c "import colorama as c; c.init(); print c.Style.BRIGHT+c.Fore.RED+'%%t did not start successfully'"
  ) else (
    echo %%t successfully started
  )
)
goto done

:killall
for %%t in (%TASKS%) do (
  schtasks /run /TN %%t_stop_%VIP_DAEMON_POSTFIX%
  call %VIP_INIT_DIR%/%%t killall
)
goto done

:stop
for %%t in (%TASKS%) do (
  schtasks /run /TN %%t_stop_%VIP_DAEMON_POSTFIX% > nul
  
  call %VIP_INIT_DIR%/%%t waitstop %VIP_DAEMON_TIMEOUT%
  if "!errorlevel!" NEQ "0" (
    python -c "import colorama as c; c.init(); print c.Style.BRIGHT+c.Fore.RED+'%%t did not stop successfully'"
    call %ELEVATE% %VIP_INIT_DIR%/%%t stop /f
    call %VIP_INIT_DIR%/%%t waitstop 2.0
  ) else (
    echo %%t is stopped
  )
)
if "%VIP_RESTART%" == "1" (
  set VIP_RESTART=
  call daemon.bat %1 start
)
goto done

:restart
set VIP_RESTART=1
goto stop
REM for %%t in (%TASKS%) do schtasks /end /TN %%t_%VIP_DAEMON_POSTFIX%
REM for %%t in (%TASKS%) do schtasks /run /TN %%t_%VIP_DAEMON_POSTFIX%
REM call daemon.bat %1 stop
REM call daemon.bat %1 start
goto done

:status
REM for %%t in (%TASKS%) do schtasks /query /TN %%t_%VIP_DAEMON_POSTFIX%
for %%t in (%TASKS%) do (
  call %VIP_INIT_DIR%/%%t.bat status
)
goto done

:test
REM for %%t in (%TASKS%) do schtasks /query /TN %%t_%VIP_DAEMON_POSTFIX%
for %%t in (%TASKS%) do (
  call %VIP_INIT_DIR%/%%t.bat test
)
goto done

:usage
echo Usages: %0 {service_name} [start^|stop^|restart^|status]
echo   where service_name can be [%VIP_SERVICES%]

:done
echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause

endlocal
