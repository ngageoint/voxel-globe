:; `dirname "$0"`/_pg_dump.bsh "${@}"; exit $?
@echo off

setlocal

call %~dp0..\vip.bat

pg_dump %VIP_POSTGRESQL_CREDENTIALS% %VIP_POSTGRESQL_DATABASE_NAME%

endlocal