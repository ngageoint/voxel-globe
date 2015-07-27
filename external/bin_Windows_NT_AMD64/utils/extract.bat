@echo off
setlocal ENABLEDELAYEDEXPANSION

set UTIL_DIR=%~dp0
if "%SZ%"=="" set SZ=%UTIL_DIR%7z.exe

for %%i in (%~n1) do set SECONDEXT=%%~xi

if /I "%~x1"==".zip" (
  goto simple
) else if /I "%~x1"==".tgz" (
  goto tar2
) else if /I "%~x1"==".gz" (
  if /I "%SECONDEXT%"==".tar" (
    goto tar2
  ) else (
    goto simple
  )
) else if /I "%~x1"==".bz2" (
  if /I "%SECONDEXT%"==".tar" (
    goto tar2
  ) else (
    goto simple
  )
) else if /I "%~x1"==".exe" (
  goto simple
) else (
  echo "Unknown extention, trying 7zip anyways..."
  goto simple
)

:tar2
SET FILENAME=%1
SHIFT
!SZ! x -so %FILENAME% | !SZ! x -y -si -ttar %1 %2 %3 %4 %5 %6 %7 %8 %9
REM Good enough, I hope!

goto done
:simple
!SZ! x -y %*

goto done
:done