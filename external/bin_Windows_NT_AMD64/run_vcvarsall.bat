@echo off
REM This is necessary because I need to call a .bat file THEN run the commands
call "%VCCARSALL%" x86_amd64
REM Apparently Windows Batch is incapable of passing arguments with | in them
REM I may not like this kind of fix, but I don't see that I have a choice. No "${@}" :(
%*