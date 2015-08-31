1>2# : ^
'''
@echo off
setlocal enabledelayedexpansion

set BUILD_DIR=%~dp0
set BUILD_DIR=%BUILD_DIR:~0,-1%
REM Since this "thing" always returns with trailing slash, remove it

call %~dp0env.bat

set TMP_DIR=%BUILD_DIR%\tmp

set PYTHON_INSTALL=%VIP_SRC_DIR%\python-2.7.10.amd64.msi

set LESSMSI=%DRYRUN%%BUILD_DIR%\utils\lessmsi.exe
set RMDIR=%DRYRUN%rmdir
set XCOPY=%DRYRUN%xcopy

mkdir %VIP_LOG_DIR:/=\% > NUL 2>&1
echo Beginning build on %DATE% > %VIP_LOG_DIR%\build.log

echo ********** Installing Python **********
%LESSMSI% x %PYTHON_INSTALL% %TMP_DIR%\ >> %VIP_LOG_DIR%\build.log
%xcopy% /Y /I /E %TMP_DIR%\SourceDir %VIP_PYTHON_DIR:/=\% >> %VIP_LOG_DIR%\build.log
%rmdir% /S /Q %VIP_PYTHON_DIR:/=\%\Windows
%rmdir% /S /Q %TMP_DIR%

REM Run the rest of the install in python. No one will ever notice!
%VIP_PYTHON_DIR%\python.exe %~dpf0

if not errorlevel 1 (
  echo Build complete! Please run setup.bat to complete installation
) else (
  echo Something went wrong with the build. Please contact a developer
)

echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause
exit /b
'''

from os.path import join as path_join
from subprocess import Popen
from distutils.dir_util import mkpath, copy_tree
from distutils.file_util import move_file, copy_file
from shutil import rmtree

import sys
import os
from glob import glob
from tempfile import mkdtemp

def addDir(dirName, fileName=None):
  if fileName:
    if not os.path.exists(path_join(dirName, fileName)):
    #In case the user specified a different path name, adding a dir will not result in a valid file
      return os.path.abspath(fileName);
    else:
      return os.path.abspath(path_join(dirName, fileName));
  else:
    return lambda x: addDir(dirName, x);
  
#Source settings
runDir=os.path.dirname(os.path.realpath(__file__));
utilDir=path_join(runDir, 'utils');
sourceDir=os.environ['VIP_SRC_DIR'];

#Destination settings
installDir=os.path.dirname(os.path.realpath(__file__));
projectRoot=os.path.realpath(path_join(installDir, '../..'));
buildDir=mkdtemp(prefix='build_', dir=runDir);
tmpDir=mkdtemp(prefix='tmp_', dir=runDir);
logDir=os.environ['VIP_LOG_DIR']

#Python
pythonDir=path_join(installDir, 'python');
python=path_join(pythonDir, 'python.exe');
pip=path_join(pythonDir, 'Scripts', 'pip.exe');

pythonPackagesSrc = ['nose-1.3.6.tar.gz',
                     'Pillow-2.8.1-cp27-none-win_amd64.whl',
                     'wxPython_common-3.0.2.0-py2-none-any.whl',
                     'wxPython-3.0.2.0-cp27-none-win_amd64.whl',
                     'numpy-1.9.2+mkl-cp27-none-win_amd64.whl',
                     'scipy-0.15.1-cp27-none-win_amd64.whl',
                     'pytz-2015.2.tar.bz2',
                     'six-1.9.0.tar.gz',
                     'python-dateutil-2.4.2.tar.gz',
                     'pandas-0.16.1-cp27-none-win_amd64.whl',
                     'sympy-0.7.6.tar.gz',
                     'backports.ssl_match_hostname-3.4.0.2.tar.gz',
                     'certifi-2015.04.28.tar.gz',
                     'tornado-4.2-cp27-none-win_amd64.whl',
                     'pyparsing-2.0.3.tar.gz',
                     'matplotlib-1.4.3-cp27-none-win_amd64.whl',
                     'pyzmq-14.6.0-cp27-none-win_amd64.whl',
                     'pyreadline-2.0.zip',
                     'MarkupSafe-0.23-cp27-none-win_amd64.whl',
                     'Jinja2-2.7.3.tar.gz',
                     'jsonschema-2.4.0.tar.gz',
                     'ptyprocess-0.4.tar.gz',
                     'terminado-0.5.tar.gz',
                     'snowballstemmer-1.2.0.tar.gz',
                     'Babel-1.3.tar.gz',
                     'alabaster-0.7.4.tar.gz',
                     'docutils-0.12.tar.gz',
                     'Pygments-2.0.2.tar.gz',
                     'colorama-0.3.3.tar.gz',
                     'sphinx_rtd_theme-0.1.8.tar.gz',
                     'Sphinx-1.3.1.tar.gz',
                     'pexpect-3.3.tar.gz',
                     'ipython-3.1.0.tar.gz',
                     'Werkzeug-0.10.4.tar.gz',
                     'itsdangerous-0.24.tar.gz',
                     'Flask-0.10.1.tar.gz',
                     'redis-py-2.10.3.tar.gz',
                     'requests-2.7.0.tar.gz',
                     'greenlet-0.4.7-cp27-none-win_amd64.whl',
                     'PyYAML-3.11.tar.gz',
                     'pystache-0.5.4.tar.gz',
                     'Markdown-2.6.2.tar.gz',
                     'gevent-1.0.2-cp27-none-win_amd64.whl',
                     'websocket-0.2.1.tar.gz',
                     'gevent-websocket-0.9.5.tar.gz',
                     'bokeh-0.9.1.tar.gz',
                     'tifffile-2014.8.24.1-cp27-none-win_amd64.whl',
                     'utm-0.4.0.tar.gz',
                     'winpdb-1.4.8.tar.gz',
                     'Django-1.8.1.tar.gz',
                     'djangorestframework-3.1.1.tar.gz',
                     'djangorestframework-gis-0.8.2.tar.gz',
                     'django-filter-0.9.2.tar.gz',
                     'django-model-utils-2.2.tar.gz',
                     'httplib2-0.9.1.tar.gz',
                     'pyrabbit-1.1.0.tar.gz',
                     'anyjson-0.3.3.tar.gz',
                     'amqp-1.4.6.tar.gz',
                     'billiard-3.3.0.20-cp27-none-win_amd64.whl',
                     'kombu-3.0.26.tar.gz',
                     'celery-3.1.18.tar.gz',
                     'futures-3.0.2.tar.gz',
                     'flower-0.8.2.tar.gz',
                     'psycopg2-2.6-cp27-none-win_amd64.whl',
                     'GDAL-1.11.2-cp27-none-win_amd64.whl',
                     'py-1.4.27.tar.gz',
                     'pytest-2.7.0.tar.gz',
                     'Mako-1.0.1.tar.gz',
                     'decorator-3.4.2.tar.gz',
                     'appdirs-1.4.0.tar.gz',
                     'pytools-2014.3.5.tar.gz',
                     'plyfile-0.4.tar.gz'];

pythonPackagesSrc=map(addDir(sourceDir), pythonPackagesSrc);

pythonPackageSetuptools = addDir(sourceDir)('setuptools-15.2.tar.gz')
pythonPackagePip = addDir(sourceDir)('pip-6.1.1.tar.gz')

#Postgres
postgresqlDir=path_join(installDir, 'postgresql');
databaseDir=path_join(projectRoot, 'data');
#postgresqlInstall=[path_join(sourceDir, 'postgresql-9.3.4-3-windows-x64.exe'), '--mode', 'unattended',
#                   '--superpassword', 'CHANGEME', 
#                   '--servicepassword', 'changeme', 
#                   '--prefix', postgresqlDir,
#                   '--datadir', databaseDir, 
#                   '--serverport', '5432', 
#                   '--locale', 'C', 
#                   '--serviceaccount', 'NT AUTHORITY\NetworkService', 
#                   '--unattendedmodeui', 'minimalWithDialogs',
#                   '--enable_acledit', '0',
#                   '--extract-only', '1'];
#For SOME reason, extract ONLY still asks for admin privileges, so I replaced it with a zip
#postgresqlZip=path_join(sourceDir, 'postgresql-9.4.2-1-windows-x64.zip');

postgisZip=path_join(sourceDir,'postgis-bundle-pg94x64-2.1.7.zip')

#Apache
apacheZip=path_join(sourceDir, 'httpd-2.4.12-x86-r2.zip');
apacheDir=path_join(runDir, 'Apache24');
apacheModules=['mod_wsgi-4.4.12-ap24-VC9-x64-py27.zip']
apacheModules=map(addDir(sourceDir), apacheModules);

#other
otherZips=[('postgresql-9.4.2-1-windows-x86.zip', '.'),
           ('redis-2.8.19.zip', '.'),
           ('rabbitmq-server-windows-3.5.3.zip', '.'),
           ('otp-17.5-amd64.zip', '.'),
           ('vips-dev-8.0.2.zip', '.'),
           ('visualsfm-0.5.26-win64.zip', '.'),
           ('vxl-2015.04.23.zip', '.'),
           ('httpd-2.4.12-x86-r2.zip', '.'),
           ('proj-4.8.0-3.tar.bz2', 'osgeo4w'),
           ('geos-3.4.2-1.tar.bz2', 'osgeo4w'),
           ('proj-datumgrid-1.5.zip', 'osgeo4w/share/proj'),
           ('mod_wsgi-4.4.12-ap24-VC9-x64-py27.zip', 'Apache24/modules')];
otherZips = map(lambda x: (addDir(sourceDir)(x[0]), x[1]), otherZips);

#util commands
extractCmd=path_join(utilDir, 'extract.bat');
#replace with python eventually

#log settings
log_out=path_join(logDir, 'build_out.log');
log_err=path_join(logDir, 'build_err.log');
log_check=path_join(logDir, 'build_check.log');

fids=dict();

def extract_src(archiveName, dirName=None):
  if not dirName:
    dirName = os.getcwd();
  mkpath(dirName);
  dirs1 = glob(path_join(dirName, '*'));
  Popen([extractCmd, archiveName, '-o'+dirName], stdout=fids['out'], stderr=fids['err']).wait();
  dirs2 = glob(path_join(dirName, '*'));
  try:
    return (set(dirs2)-set(dirs1)).pop(); #Return first new dir
  except:
    return None

def python_build_install(srcDir):
  Popen([python, './setup.py', 'build'], stdout=fids['out'], stderr=fids['err'], cwd=srcDir).wait();
  Popen([python, './setup.py', 'check'], stdout=fids['check'], stderr=fids['check'], cwd=srcDir).wait();
  Popen([python, './setup.py', 'install'], stdout=fids['out'], stderr=fids['err'], cwd=srcDir).wait();
#  populate_roam

def python_all(archiveName, extractDir=None):
  print "Extracting %s" % archiveName
  srcDir = extract_src(archiveName, extractDir);
  print "Building %s" % srcDir;
  python_build_install(srcDir);

def pip_install(package_name):
  Popen([pip, '--proxy=127.0.0.0:0', 'install', '--no-deps', '--disable-pip-version-check', package_name], stdout=fids['out'], stderr=fids['err']).wait();
#  Popen([pip, '--proxy=127.0.0.0:0', 'install', '--disable-pip-version-check', package_name], stdout=fids['out'], stderr=fids['err']).wait();

if __name__=='__main__':
  fids['out'] = open(log_out, 'w');
  fids['err'] = open(log_err, 'w');
  fids['check'] = open(log_check, 'w');
  pids = [];
  
  stdout=sys.stdout;
  sys.stdout=fids['out'];
  sys.stderr=fids['err'];

  print >>stdout, '********** Installing Python Packages **********'
  print >>stdout, 'Installing Setuptools'
  python_all(pythonPackageSetuptools, extractDir=buildDir);
  print >>stdout, 'Installing Pip'
  python_all(pythonPackagePip, extractDir=buildDir);

  for package in pythonPackagesSrc:
    print >>stdout, "Pip Installing", package
    pip_install(package);
  
  for (filename, destDir) in otherZips:
    print >>stdout, '********** Installing %s **********' % os.path.split(filename)[1]
    extract_src(filename, os.path.join(installDir, destDir))

  # print >>stdout, '********** Installing Apache Modules **********'
  # os.chdir(path_join(apacheDir, 'modules'));
  # for filename in apacheModules:
    # pids.append(Popen([extractCmd, filename], stdout=fids['out'], stderr=fids['err'])); pids.pop().wait()
    
  # os.chdir(installDir);
    
  print '********** Juggling directories and files **********'
  os.rename(os.path.join(runDir, glob('vips*')[0]), os.path.join(runDir, 'vips'))
  os.rename(os.path.join(runDir, glob('rabbitmq_server*')[0]), os.path.join(runDir, 'rabbitmq_server'))
  move_file(os.path.join(runDir, 'readme_first.html'), os.path.join(runDir, 'Apache24'))

  # On Nvidia systems, the DLL is called OpenCL64.dll when it needs to be OpenCL.dll
  try:
    copy_file(env['VIP_OPENCL_DLL'], path_join(env['VIP_VXL_DIR'], 'OpenCL.dll'))
  except:
    print 'VIP_OPENCL_DLL not found'

  #Install cuda version
  if os.environ['VIP_VISUALSFM_CUDA'] == '1':
    for filename in glob(os.path.join(installDir, 'visualsfm', 'cuda', '*')):
      copy_file(filename, os.path.join(installDir, 'visualsfm'))

  print >>stdout, '********** Installing Postgis **********'
  mkpath(tmpDir);
  pid = Popen([extractCmd, postgisZip, '-o'+tmpDir], stdout=fids['out'], stderr=fids['err']); pid.wait();
  copy_tree(glob(path_join(tmpDir, '*'))[0], postgresqlDir);
  rmtree(tmpDir);
      
  print '********** Patching Erlang ini files **********'
  for root, dirs, files in os.walk(os.environ['VIP_RABBITMQ_ERLANG_HOME']):
    if 'erlexec.dll' in files:
      erlang_bindir = root;
      break;
  for root, dirs, files in os.walk(os.environ['VIP_RABBITMQ_ERLANG_HOME']):
    if 'erl.ini' in files:
       print path_join(root, 'erl.ini')
       with open(path_join(root, 'erl.ini'), 'wb') as fid:
       #Hey, the original files are \n only, so SO are mine!
         fid.write('[erlang]\nBindir=%s\nProgname=erl\nRootdir=%s\n' % 
              (os.path.realpath(erlang_bindir).replace('\\', '\\\\'), 
              os.path.realpath(os.environ['VIP_RABBITMQ_ERLANG_HOME']).replace('\\', '\\\\')))
  
 
  print >>stdout, '********** Installing External Data **********'
  copy_file(path_join(os.environ['VIP_EXTERNAL_DATA_DIR'], 'egm96_15.gtx'), os.environ['VIP_DJANGO_PROJ_LIB']);

  print >>stdout, '********** Cleaning up **********'
  rmtree(buildDir);
