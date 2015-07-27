1>2# : ^
'''
@echo off
setlocal
call %~dp0/env.bat
call %VIP_LOCAL_SETTINGS% %*

call %VIP_INSTALL_DIR%/elevate.bat %~f0 %*
if not %errorLevel% == 3 exit /b

%VIP_PYTHON_DIR%/python %~f0
echo Setup complete! Please run initialize_database.bat to complete database setup
echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause
exit /b
endlocal
'''

#Groovy batch wrapped python script

import os
import sys
import re
from os.path import join as path_join
from subprocess import Popen, PIPE
from distutils.dir_util import mkpath
import tempfile;
import time;
import _winreg;
import itertools

def addDir(dirName, fileName=None):
  if fileName:
    if not os.path.exists(path_join(dirName, fileName)):
    #In case the user specified a different path name, adding a dir will not result in a valid file
      return os.path.abspath(fileName);
    else:
      return os.path.abspath(path_join(dirName, fileName));
  else:
    return lambda x: addDir(dirName, x);

scriptDir=os.path.dirname(os.path.realpath(__file__));
tempFileName = os.path.join(scriptDir, 'pyGetPrivileges.vbs');
installerDir=os.environ['VIP_SRC_DIR'];

#Redistributables
#'vcredist_2008_x64.exe',
redistributables=[['vcredist_2008_sp1_x64.exe','/q'],###AEN
                  ['vcredist_2010_x64.exe', '/q'],
                  ['vcredist_2012u4_x64.exe', '/passive', '/norestart'],
                  ['vcredist_2013_x64.exe', '/passive', '/norestart']];
redistributableKeys = [[_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall', '{5FCE6D76-F5DC-37AB-B2B8-22AB8CEDB1D4}'],
                       [_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall', '{1D8E6291-B0D5-35EC-8441-6616F567A0F7}'],
                       [_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall', '{CF2BEA3C-26EA-32F8-AA9B-331F7E34BA97}'],
                       [_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall', '{050d4fc8-5d48-4b8f-8972-47c82c46020f}']]
#redistributables_arguments=['/q', '/q', ['/passive', '/norestart']]
#redistributables=map(addDir(installerDir), redistributables);
#redistributables=map(lambda x:list(itertools.chain(*x)), zip(redistributables, redistributables_arguments));
redistributables=map(lambda x: [addDir(installerDir, x[0])]+x[1:], redistributables);

def changeXml(xml, element, stringValue):
  return re.sub(r'<%s>.*?</%s>' % (element, element), r'<%s>%s</%s>' % (element, stringValue, element),  xml);

def createWindows7Task(taskName, taskCommand):
  cmd = ['schtasks', '/create', 
         '/TN', taskName, 
         '/SC', 'onstart',
         '/TR', taskCommand, 
         '/RL', 'HIGHEST', '/F']; #Create task as the installer
#         '/RU', 'NT AUTHORITY\NETWORKSERVICE', '/F'];
  '''if os.environ['VIP_AUTOSTART'] == '1':
    cmd += ['/sc', 'onstart']
  else:
    cmd += ['/sc', 'once']'''
  Popen(cmd).wait()
  xml=Popen(['schtasks', '/query', 
             '/TN', taskName, '/xml'], stdout=PIPE).communicate()[0];
  xml=changeXml(xml, 'DisallowStartIfOnBatteries', 'false');
  xml=changeXml(xml, 'StopIfGoingOnBatteries', 'false');
  xml=changeXml(xml, 'AllowHardTerminate', 'true');
  xml=changeXml(xml, 'ExecutionTimeLimit', 'PT0S');
  if not os.environ['VIP_AUTOSTART'] == '1':
    xml=re.sub(r'(<%s>.*?<%s>).*?(</%s>.*?</%s>)' % 
                 ('BootTrigger', 'Enabled', 'Enabled', 'BootTrigger'), 
               r'\1%s\2' % 'false', xml, flags=re.DOTALL)
  fid = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xml');
  fid.write(xml);
  fid.close();
  Popen(['schtasks', '/create', '/TN', taskName, '/xml', fid.name, '/F']).wait();
  os.remove(fid.name);

def addFirewallRule(ruleName, programPath):
  Popen(['netsh', 'advfirewall', 'firewall', 'add', 'rule', 
         'name="%s"'%ruleName, 'dir=in', 'action=allow',
         'program="%s"'%programPath, 'profile=Domain,Private,Public']).wait();

if __name__=='__main__':
  print '********** Installing Redistributables **********'
  pids=[];
  for redistributable in range(len(redistributables)):
    alreadyInstalled = False;
    regKey = _winreg.OpenKey(redistributableKeys[redistributable][0], redistributableKeys[redistributable][1]);
    i = 0;
    try:
      while 1:
        if _winreg.EnumKey(regKey, i) == redistributableKeys[redistributable][2]:
          alreadyInstalled = True;
          break;
        i+=1;
    except WindowsError:
      pass;
    finally:
      _winreg.CloseKey(regKey);

    if not alreadyInstalled:
      print redistributables[redistributable]
      pids.append(Popen(redistributables[redistributable]))
      pids.pop().wait()

  for task in os.environ['VIP_SERVICES'].split(' '):
    print '********** Setting up %s daemon **********' % task
    createWindows7Task(task+'_start_'+os.environ['VIP_DAEMON_POSTFIX'], 
                       '%s/pythonw.exe %s/bg.py %s/%s.bat start' % (
                                       os.environ['VIP_PYTHON_DIR'],
                                       os.environ['VIP_INIT_DIR'],
                                       os.environ['VIP_INIT_DIR'],
                                       task));
    createWindows7Task(task+'_stop_'+os.environ['VIP_DAEMON_POSTFIX'], 
                       '%s/pythonw.exe %s/bg.py %s/%s.bat stop' % (
                                       os.environ['VIP_PYTHON_DIR'],
                                       os.environ['VIP_INIT_DIR'],
                                       os.environ['VIP_INIT_DIR'],
                                       task));

  print '********** Setting up firewall rules **********'
  addFirewallRule(os.environ['VIP_FIREWALL_RULE_NAME'], os.path.normpath(path_join(os.environ['VIP_PYTHON_DIR'], 'python.exe')));
  addFirewallRule(os.environ['VIP_FIREWALL_RULE_NAME'], os.path.normpath(path_join(os.environ['VIP_PYTHON_DIR'], 'Scripts', 'ipython.exe')));
  addFirewallRule(os.environ['VIP_FIREWALL_RULE_NAME'], os.path.normpath(path_join(os.environ['VIP_POSTGRESQL_DIR'], 'bin', 'postgres.exe')));
  addFirewallRule(os.environ['VIP_FIREWALL_RULE_NAME'], os.path.normpath(path_join(os.environ['VIP_HTTPD_DIR'], 'bin', 'httpd.exe')));
  addFirewallRule(os.environ['VIP_FIREWALL_RULE_NAME'], os.path.normpath(path_join(os.environ['VIP_RABBITMQ_ERLANG_HOME'], 'bin', 'erl.exe')));
  addFirewallRule(os.environ['VIP_FIREWALL_RULE_NAME'], os.path.normpath(path_join(os.environ['VIP_PYTHON_DIR'], 'pythonw.exe')));
  addFirewallRule(os.environ['VIP_FIREWALL_RULE_NAME'], os.path.normpath(path_join(os.environ['VIP_RABBITMQ_ERLANG_HOME'], 'erts-6.4', 'bin', 'epmd.exe')));
  addFirewallRule(os.environ['VIP_FIREWALL_RULE_NAME'], os.path.normpath(path_join(os.environ['VIP_RABBITMQ_ERLANG_HOME'], 'erts-6.4', 'bin', 'erl.exe')));
# I'm not 100% sure the last two are needed (or if the last one is "secure"), but in case it IS needed, it's here

  print '********** Setting up other directories **********'
  mkpath(os.environ['VIP_LOG_DIR'])
  fid = open(os.environ['VIP_BASE_SCRIPT'], 'w')
  fid.write('''@echo off
REM DO NOT EDIT THIS AUTO GENERATED FILE! Edit %s instead
call %%~dp0%s\env.bat %%*\n''' % (os.path.split(os.environ['VIP_LOCAL_SETTINGS'])[1], 
                                  os.path.relpath(os.environ['VIP_INSTALL_DIR'], 
                                                  os.environ['VIP_PROJECT_ROOT'])))
  fid.close()
  
  if not os.path.exists(os.environ['VIP_LOCAL_SETTINGS']):
    with open(os.environ['VIP_LOCAL_SETTINGS'], 'w') as fid:
      fid.write('REM Add local setting here')

  print "Setup complete!"
  #import getpass; getpass.getpass(prompt='All done. Press enter to continue');
