:; `dirname "$0"`/_pg_restore.bsh "${@}"; exit $?
@echo off

setlocal

call %~dp0..\vip.bat

dropdb %VIP_POSTGRESQL_CREDENTIALS% %VIP_POSTGRESQL_DATABASE_NAME%

pg_restore %VIP_POSTGRESQL_CREDENTIALS% -d %VIP_POSTGRESQL_DATABASE_NAME% %*

endlocal