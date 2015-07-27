1>2# : ^
'''
@echo off
net session >nul 2>&1
if not %errorLevel% == 0 (
  if "%attemptElevate%" NEQ "1" (
  REM This gate isn't working! :(
    set attemptElevate=1

    setlocal enabledelayedexpansion
    call %~dp0base.bat
    call !VIP_BASE_SCRIPT!
    !VIP_PYTHON_DIR!/python %~f0 %*
    echo !errorlevel!
    REM Since this is called by a batch/python hybrid, end now!
    endlocal
    set attemptElevate=
    exit /b 1
  ) else (
    REM I don't think I can ever get here...
    echo ERROR: Elevation of permissinos FAILED. I will attempt to run the command anyway ^
but it will probably fail. Please make sure you are running from an user account ^
that has the capability of elevate ^(UAC permissions^), not neccesarily an ^
admin account.
    set attemptElevate=
    exit /b 2
  )
)
exit /b 3
'''

import os
import subprocess
import sys

if __name__=='__main__':
  tmpfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'OEgetPrivileges.vbs')
  if len(sys.argv)>2:
    args = ' '.join(sys.argv[2:])
  else:
    args = ''
  with open(tmpfile, 'w') as fid:
    #print 'Elevated permissions...'
    print >>fid, 'Set UAC = CreateObject("Shell.Application")'
    print >>fid, 'UAC.ShellExecute "%s", "%s", "", "runas", 1' % (sys.argv[1], args)
    #This probably isn't good enough, need to use bg.py and bg2.py to fix this, or use pywin32
  #os.environ['attemptElevate'] = '1' #Does not work. The current problem is still, I can't
  #determine if the elevation call fails or not. Once I start using pywin32 instead, maybe I
  #can get this working... Maybe. At any rate, right now, if you try this from a program that 
  #calls itself from a user with no permission to elevate, you'll get an infinite loop of
  #command prompts popping up. :(
  pid = subprocess.Popen(['wscript', '//b', tmpfile])#, env=os.environ)
  pid.wait()
  os.remove(tmpfile)
  exit(pid.returncode)