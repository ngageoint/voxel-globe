:; $(dirname $0)/_install.bsh "${@}"; exit $?
@echo off

setlocal

call :echoc "Would you like to \[5]play\[7] a \[7C]game"
call :ask ans1 "? "

echo Ans1 is %ans1%

endlocal

goto :eof

:tryagain
echo Please enter yes or no (y/n)

:ask
set /p ans=%2
if "%ans%"=="" goto :tryagain
if /i "%ans:~0,1%" == "y" ( set %1=1 ) else ( if /i "%ans:~0,1%" == "n" ( set %1=0 ) else ( goto :tryagain ) )
set ans=

goto :eof

:split
set str=%~1
set post=%str:*\[=%
if "%post%" == "%str%" (
  set pre=%post%
  set post=
) else (
  set pre=!str:\[%post%=!
)

if "%post:~1,1%" == "]" ( 
  set color_use=%post:~0,1%
  set post=%post:~2%
) else if "%post:~2,1%" == "]" (
  set color_use=%post:~0,2%
  set post=%post:~3%
)
REM This Recursion can't be made to work in batch. Same variable names, etc...
REM All very difficult. If it's possible, I decided not to try. I CAN use this
REM code, however there will be a color gap. Doing it right seemed... fixing
REM that color gap seemed... difficult
REM else (
REM   set color_use=
REM   set pre=%pre%\[ 
REM   REM ELSE add it back in
REM )

exit /b

:echoc

SETLOCAL enabledelayedexpansion
call :split "%~1"

call :echonn "%pre%"

call :echoc_recurse

endlocal
exit /b

:echoc_recurse
REM Save the color code from the initial split
set color1=%color_use%

REM Split again
call :split "%post%"

REM if there was a color, print it ,else normal echo
if "%color_1" NEQ "" (
  call :colorPrint %color1% "%pre%"
) else (
  call :echonn "%pre%"
)

if "%post%" NEQ "" (
  call :echoc_recurse "%post%"
)

exit /b

:echonn
<nul set /p="%~1"
exit /b

REM http://stackoverflow.com/questions/4339649/how-to-have-multiple-colors-in-a-windows-batch-file/10407642
:colorPrint Color  Str  [/n]
setlocal
set "str=%~2"
call :colorPrintVar %1 str %3
endlocal
exit /b

:colorPrintVar  Color  StrVar  [/n]
if not defined %~2 exit /b
setlocal enableDelayedExpansion
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do set "DEL=%%a"
<nul >"%temp%\~" set /p "=%DEL%%DEL%%DEL%%DEL%%DEL%%DEL%.%DEL%"
set "str=a%DEL%!%~2:\=a%DEL%\..\%DEL%%DEL%%DEL%!"
set "str=!str:/=a%DEL%/..\%DEL%%DEL%%DEL%!"
set "str=!str:"=\"!"
pushd "%temp%"
findstr /p /A:%1 "." "!str!\..\~" nul
if /i "%~3"=="/n" echo(
del "%temp%\~"
endlocal
exit /b
