1>2# : ^
'''
@echo off
%~dp0sysv.bat %~f0 %*
'''

from sysv import Simple, SysVCli, SysV
from os import environ as env
import shlex
import subprocess
import os

class Postgresql(Simple, SysVCli):
  def __init__(self):
    self.name = 'postgresql'
    self.cmd = ['postgres', '-D', env['VIP_POSTGRESQL_DATABASE']]+\
               shlex.split(env['VIP_POSTGRESQL_SERVER_CREDENTIALS'])

    self.user = env.pop('VIP_DAEMON_USER', None)

    self.registerTestCli(self.testCli)
    
    super(Postgresql, self).__init__()

  def stop(self, force=False):
    if force:
      return super(Postgresql, self).stop(force=force)
    else:
      with open(os.path.join(env['VIP_POSTGRESQL_LOG_DIR'], 'postgresql_stop.log'), 'w') as fid:
        pid = subprocess.Popen(['pg_ctl', 'stop', '-D', env['VIP_POSTGRESQL_DATABASE'], '-m', 'fast'],
                               stdout=fid, stderr=subprocess.STDOUT, stdin=open(os.devnull, 'r'))
        
      return (pid.wait()==0, self.getPid())

  def test(self):
    pid = subprocess.Popen(['pg_isready'] + shlex.split(env['VIP_POSTGRESQL_CREDENTIALS']),
                            stdout=open(os.devnull, 'w'), 
                            stderr=subprocess.STDOUT, 
                            stdin=open(os.devnull, 'r'))
    return pid.wait()

if __name__=='__main__':
  Postgresql().cli()