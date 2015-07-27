:; `dirname "$0"`/_wrap.bsh "${@}"; exit $?
@echo off
setlocal enabledelayedexpansion

call %~dp0vip.bat %*

if "%VIP_NARG%" == "0" (
  %~d0
  REM swtich to that drive (c: or other)
  cd %~dp0
  REM cd script dir
)

call %VIP_INSTALL_DIR%/wrap.bat %*

endlocal
