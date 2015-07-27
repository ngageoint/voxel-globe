@echo off
setlocal enabledelayedexpansion

call %~dp0env.bat

set PIP_DIR=%VIP_PYTHON_DIR:/=\%\pip

set PYTHONPATH=%PIP_DIR%\Lib\site-packages;%PYTHONPATH%

if not exist %PIP_DIR% (
  REM INSTALL Pip
  mkdir %PIP_DIR%\Lib\site-packages
  easy_install --prefix=%PIP_DIR% pip
)

%PIP_DIR%\Scripts\pip %* --no-compile --download-cache %PIP_DIR%\cache --install-option="--prefix=%PIP_DIR%\stage" --no-use-wheel

if not errorlevel 1 (
  mkdir %PIP_DIR%\stage\dist

  move %PIP_DIR%\stage\Lib\site-packages %PIP_DIR%\stage\dist\PLATLIB
  rmdir %PIP_DIR%\stage\Lib

  if exist %PIP_DIR%\stage\Scripts move %PIP_DIR%\stage\Scripts %PIP_DIR%\stage\dist\SCRIPTS

  for %%i in (%PIP_DIR%\stage\*) do (
    mkdir %PIP_DIR%\stage\dist\DATA
    move %%i %PIP_DIR%\stage\dist\DATA
  )


  cd %PIP_DIR%\stage\dist

  7z a %~dp0package.zip *

  cd %~dp0

  rmdir /Q /S %PIP_DIR%\stage
)
endlocal