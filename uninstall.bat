:; $(dirname $0)/_uninstall.bsh "${@}"; exit $?
@echo off

setlocal

call :ask ans1 "Would you like to play a game? "

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

