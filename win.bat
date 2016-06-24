@echo off
setlocal enabledelayedexpansion
call bash %~dp0wrap %*
endlocal
