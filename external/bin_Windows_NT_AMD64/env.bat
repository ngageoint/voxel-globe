@echo off
REM do NOT setlocal in here

set VIP_NARG=0
for %%x in (%*) do Set /A VIP_NARG+=1
REM Always do the arg count

if "%VIP%"=="2" goto :eol
::Prevent multiple calls, it was just breaking the PATH variable mostly

call %~dp0base.bat

if not defined VIP_LOCAL_SETTINGS set VIP_LOCAL_SETTINGS=%VIP_PROJECT_ROOT%/local_vip.bat

if exist %VIP_LOCAL_SETTINGS% call %VIP_LOCAL_SETTINGS%

set VIP=2
REM Prevents double Calling above

if not defined VIP_WRAP_SCRIPT set VIP_WRAP_SCRIPT=%VIP_PROJECT_ROOT%/wrap.bat

if not defined VIP_DAEMON_USER set VIP_DAEMON_USER=NT AUTHORITY\NETWORK SERVICE
if not defined VIP_DAEMON_BACKGROUND set VIP_DAEMON_BACKGROUND=1

if not defined VIP_INSTALL_DIR set VIP_INSTALL_DIR=%~dp0
REM Since this "thing" always returns with trailing slash, remove it
if not defined VIP_INSTALL_DIR set VIP_INSTALL_DIR=%VIP_INSTALL_DIR:~0,-1%
if not defined VIP_INSTALL_DIR set VIP_INSTALL_DIR=%VIP_INSTALL_DIR:\=/%
if not defined VIP_SRC_DIR set VIP_SRC_DIR=%VIP_INSTALL_DIR%/../src/SOURCES
if not defined VIP_INIT_DIR set VIP_INIT_DIR=%VIP_INSTALL_DIR%/init.d
if not defined VIP_OS set VIP_OS=%OS%
if not defined VIP_ARCH set VIP_ARCH=%PROCESSOR_ARCHITECTURE%

if not defined VIP_PID_DIR set VIP_PID_DIR=%VIP_PROJECT_ROOT%/logs

REM ##### VXL var #####
REM THIS NEXT LINE SHOULDN'T SAY VXL!!! It should use %VIP_VXL_BUILD_DIR%!!!! chickenegg
if not defined VIP_GLEW_DIR set VIP_GLEW_DIR=%VIP_PROJECT_ROOT%/external/vxl/glew-1.12.0
if not defined VIP_GLEW_INCLUDE_DIR set VIP_GLEW_INCLUDE_DIR=%VIP_GLEW_DIR%/include
if not defined VIP_GLEW_LIBRARY set VIP_GLEW_LIBRARY=%VIP_GLEW_DIR%/lib/Release/x64/glew32.lib
if not defined VIP_GLEW_BIN_DIR set VIP_GLEW_BIN_DIR=%VIP_GLEW_DIR%/bin/Release/x64
REM set VIP_CMAKE_PLATFORM="" Specify in local env file!
if not defined VIP_VXL_DIR set VIP_VXL_DIR=%VIP_INSTALL_DIR%/vxl
if not defined VIP_VXL_PYTHON_DIR set VIP_VXL_PYTHON_DIR=%VIP_VXL_DIR%/lib/python2.7/site-packages/vxl
if not defined VIP_VXL_BIN_DIR set VIP_VXL_BIN_DIR=%VIP_VXL_DIR%/bin
if not defined VIP_VXL_SHARE_DIR set VIP_VXL_SHARE_DIR=%VIP_VXL_DIR%/share

if defined CUDA_PATH (
  if not defined VIP_OPENCL_INCLUDE_PATH set VIP_OPENCL_INCLUDE_PATH=%CUDA_PATH%\include
  if not defined VIP_OPENCL_LIBRARY_PATH set VIP_OPENCL_LIBRARY_PATH=%CUDA_PATH%\lib\x64
  REM set VIP_OPENCL_LIBRARY=%VIP_OPENCL_LIBRARY_PATH%\OpenCl.lib
  REM set VIP_OPENCL_LIBRARY_PATH=C:\Program Files\NVIDIA Corporation\OpenCL
  REM set VIP_OPENCL_LIBRARY=%VIP_OPENCL_LIBRARY_PATH%\OpenCl.dll
  if not defined VIP_OPENCL_DLL set VIP_OPENCL_DLL=C:\Program Files\NVIDIA Corporation\OpenCL\OpenCL64.dll
) else if defined INTELOCLPATH (
  if not defined VIP_OPENCL_INCLUDE_PATH set VIP_OPENCL_INCLUDE_PATH=%INTELOCLPATH%\..\..\include
  if not defined VIP_OPENCL_LIBRARY_PATH set VIP_OPENCL_LIBRARY_PATH=%INTELOCLPATH%\..\lib\x64
  REM set VIP_OPENCL_LIBRARY=%VIP_OPENCL_LIBRARY_PATH%\OpenCl.lib
  REM set VIP_OPENCL_LIBRARY=%SYSTEMROOT%\system32\OpenCl.dll
  REM Yep, that's where intel puts it
)

REM ##### PYTHON var #####
if not defined VIP_PYTHON_DIR set VIP_PYTHON_DIR=%VIP_INSTALL_DIR%/python
if not defined VIP_PYTHON_INCLUDE_DIR set VIP_PYTHON_INCLUDE_DIR=%VIP_PYTHON_DIR%/include
if not defined VIP_PYTHON_LIBRARY set VIP_PYTHON_LIBRARY=%VIP_PYTHON_DIR%/libs/python27.lib
if not defined VIP_PYTHON_EXECUTABLE set VIP_PYTHON_EXECUTABLE=%VIP_PYTHON_DIR%/python.exe
if not defined VIP_PYTHONW_EXECUTABLE set VIP_PYTHONW_EXECUTABLE=%VIP_PYTHON_DIR%/pythonw.exe
REM set VIP_NOTEBOOK_USER=%USERNAME%
REM set VIP_NOTEBOOK_RUN_DIR=%HOMEDRIVE%%HOMEPATH%/notebook

REM ##### GEODJANGO var #####
if not defined VIP_DJANGO_GEODJANGO_DLLS set VIP_DJANGO_GEODJANGO_DLLS=%VIP_INSTALL_DIR%/osgeo4w/bin
if not defined VIP_DJANGO_PROJ_LIB set VIP_DJANGO_PROJ_LIB=%VIP_INSTALL_DIR%/osgeo4w/share/proj
if not defined VIP_DJANGO_GDAL_LIBRARY_PATH set VIP_DJANGO_GDAL_LIBRARY_PATH=%VIP_PYTHON_DIR%/Lib/site-packages/osgeo/gdal111.dll
if not defined VIP_DJANGO_GEOS_LIBRARY_PATH set VIP_DJANGO_GEOS_LIBRARY_PATH=%VIP_DJANGO_GEODJANGO_DLLS%/geos_c.dll
if not defined VIP_DJANGO_GDAL_DATA set VIP_DJANGO_GDAL_DATA=%VIP_PYTHON_DIR%/Lib/site-packages/osgeo/data/gdal

REM ##### POSTGRESQL var #####
if not defined VIP_POSTGRESQL_LOCALE set VIP_POSTGRESQL_LOCALE=English_US.1252

REM ##### CELERY vars #####
if not defined VIP_VISUALSFM_EXE set VIP_VISUALSFM_EXE=%VIP_INSTALL_DIR%/visualsfm/VisualSFM.exe
REM to 1 to enable
if not defined VIP_VISUALSFM_CUDA set VIP_VISUALSFM_CUDA=0

REM ##### RABITMQ vars ##### 
if not defined VIP_RABBITMQ_DIR set VIP_RABBITMQ_DIR=%VIP_INSTALL_DIR%/rabbitmq_server
if not defined VIP_RABBITMQ_ERLANG_HOME set VIP_RABBITMQ_ERLANG_HOME=%VIP_INSTALL_DIR%/erlang
REM don't need this in path. RabbitMQ can find it as long as this var is set
if not defined VIP_RABBITMQ_DAEMON set VIP_RABBITMQ_DAEMON=epmd.exe

if not defined VIP_NUMBER_CORES set VIP_NUMBER_CORES=%NUMBER_OF_PROCESSORS%

REM ##### Apache HTTPD vars ##### 
if not defined VIP_HTTPD_SERVERROOT_BASE set VIP_HTTPD_SERVERROOT_BASE=%VIP_INSTALL_DIR%
if not defined VIP_HTTPD_DIR set VIP_HTTPD_DIR=%VIP_HTTPD_SERVERROOT_BASE%/Apache24

REM *********** NON-VIP Section. There can affect ANYTHING ***********
REM These parameters are not protected by the VIP Prefix, and thus
REM Affect many application, but hopefully in a good way :)

REM Load common parameters used in Linux too
call %VIP_PROJECT_ROOT:/=\%\common.bat

REM call %VIP_VSI_DIR:/=\%\env.bat Too non-intrusive

if defined PATH set PATH=%PATH%;%VIP_VSI_DIR%/windows
if not defined PATH set PATH=%VIP_VSI_DIR%/windows

if defined PYTHONPATH (
  set PYTHONPATH=%VIP_VSI_DIR%/python;%PYTHONPATH%
) else (
  set PYTHONPATH=%VIP_VSI_DIR%/python
)

REM Different in windows, so can't be in common :(
if not defined VIP_VXL_BUILD_LIB_DIR set VIP_VXL_BUILD_LIB_DIR=%VIP_VXL_BUILD_DIR%/%VIP_VXL_BUILD_TYPE%/lib/%VIP_VXL_BUILD_TYPE%
if not defined VIP_VXL_BUILD_BIN_DIR set VIP_VXL_BUILD_BIN_DIR=%VIP_VXL_BUILD_DIR%/%VIP_VXL_BUILD_TYPE%/bin/%VIP_VXL_BUILD_TYPE%
if not defined VIP_PYTHONPATH set VIP_PYTHONPATH=%VIP_PYTHONPATH%;%VIP_VXL_PYTHON_DIR%

REM It's not that these are different in Windows and Linux, more that it's different when DEPLOYED in windows
if not defined BOXM2_OPENCL_DIR set BOXM2_OPENCL_DIR=%VIP_VXL_DIR%/share/vxl/cl/boxm2
if not defined VOLM_DIR set VOLM_DIR=%VIP_VXL_DIR%/share/vxl

REM Special Windows Crap
for %%x in (%VIP_DATABASE_DIR%) do (
  if not defined VIP_RABBITMQ_BASE_DRIVE set VIP_RABBITMQ_BASE_DRIVE=%%~dx
  if not defined VIP_RABBITMQ_BASE_PATH set VIP_RABBITMQ_BASE_PATH=%%~pnxx
)

if not defined RABBITMQ_BASE set RABBITMQ_BASE=%VIP_PROJECT_ROOT%
if not defined RABBITMQ_LOG_BASE set RABBITMQ_LOG_BASE=%VIP_RABBITMQ_LOG_DIR%
if not defined RABBITMQ_MNESIA_BASE set RABBITMQ_MNESIA_BASE=%VIP_RABBITMQ_MNESIA_BASE%
if not defined RABBITMQ_PID_FILE set RABBITMQ_PID_FILE=%VIP_RABBITMQ_PID_FILE%
if not defined ERLANG_HOME set ERLANG_HOME=%VIP_RABBITMQ_ERLANG_HOME%
REM These have huge implications for the rest of the infrastructure, although
REM it is NEEDED for rabbitmq to work correctly, it will probably change where
REM everything thinks the home dir is, which is probably good.
if not defined HOMEDRIVE set HOMEDRIVE=%VIP_RABBITMQ_BASE_DRIVE%
if not defined HOMEPATH set HOMEPATH=%VIP_RABBITMQ_BASE_PATH%
REM set TEMP=%HOMEDRIVE%%HOMEPATH%\Temp
REM set LOCALAPPDATA=%HOMEDRIVE%%HOMEPATH%\Local
REM set APPDATA=%HOMEDRIVE%%HOMEPATH%\Roaming
REM set TMP=%TEMP%
REM set USERPROFILE=%HOMEDRIVE%%HOMEPATH%

if defined PYTHONPATH (
  set PYTHONPATH=%VIP_PYTHONPATH%;%PYTHONPATH%
) else (
  set PYTHONPATH=%VIP_PYTHONPATH%
)

set PATH=%VIP_UTIL_DIR%;%VIP_POSTGRESQL_DIR%/bin;%VIP_HTTPD_DIR%/bin;%VIP_PYTHON_DIR%;%VIP_PYTHON_DIR%/Scripts;%VIP_PYTHON_DIR%/Lib/site-packages/osgeo;%VIP_RABBITMQ_DIR%/sbin;%VIP_DJANGO_GEODJANGO_DLLS%;%VIP_INSTALL_DIR%/vips/bin;%VIP_INSTALL_DIR%/vxl/bin;%PATH%
