@echo off

setlocal 

call %~dp0env.bat %*
REM I'm pretty sure this line is necessary for some NARG reason

if "%VIP_NARG%" == "0" (
  set PROMPT=%VIP_PROJECT_NAME% $P$G
  start cmd
) else (
  REM In case no arguments, this REM is needed
  call %*
)

endlocal
