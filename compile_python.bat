:; cmd=($(dirname $0)/_wrap.bsh python -x $0 "${@}"); if [[ $(id -u) == 0 ]]; then if [ "${SUDO_UID:+blah}" == "" ]; then SUDO_UID=$(stat -c %u voxel_globe); fi; sudo -E -u \#${SUDO_UID} "${cmd[@]}"; else "${cmd[@]}"; fi; exit $?; ^
'''
@echo off
call %~dp0\wrap.bat python -x %~dp0%~nx0 %*

echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause
goto :eof
'''

import compileall
from os import environ as env

if __name__=='__main__':
  compileall.compile_dir(env['VIP_VSI_DIR'], quiet=True)
  compileall.compile_dir(env['VIP_DJANGO_PROJECT'], quiet=True)