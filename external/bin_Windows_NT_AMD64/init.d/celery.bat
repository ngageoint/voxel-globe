1>2# : ^
'''
@echo off
%~dp0sysv.bat %~f0 %*
'''

from sysv import SimpleDaemon, SysVCli
from os import environ as env
from posixpath import join as pathjoin
from subprocess import Popen, STDOUT, call
import os

class Celeryd(SimpleDaemon, SysVCli):
  def __init__(self):
    self.name = 'celeryd'
    self.cmd = ['celery', 'worker', '-A', env['VIP_CELERY_APP'],
                '--maxtasksperchild=1',
                '--logfile=%s' % pathjoin(env['VIP_CELERY_LOG_DIR'],'celery_log.log'),
                '--loglevel=%s' % env['VIP_CELERY_LOG_LEVEL']]

    self.user = env.pop('VIP_DAEMON_USER', None)
    
    self.registerTestCli()
    self.registerCli(self.daemonCli)
    self.registerCli(self.killAllCli)

    super(Celeryd, self).__init__()

  def test(self):
    pid = Popen(['celery', 'status'], 
                stdout=open(os.devnull, 'w'), 
                stderr=STDOUT, 
                stdin=open(os.devnull, 'r'))
    return pid.wait()
    
  def daemonCli(self):
    ''' Creates the daemon environment and runs the command
    
        This should only be called by the start CLI. You should not be calling
        this (except maybe for debugging purposes)'''
    env['VIP_DJANGO_DEBUG']=env['VIP_CELERY_DJANGO_DEBUG']
    #Use Celery's Debug flag for this
    if env['VIP_CELERY_AUTORELOAD'] == '1':
      self.cmd += ['--autoreload']
    return self.daemon()
  daemonCli.name = 'daemon'
  daemonCli.help = 'This is the actual command called to start celeryd. You should not be calling this directly'

  def killAllCli(self):
    ''' Kill all celeryd server pids

        This will attempt to kill all celery processes running, 
        regardless of how they were started. This mean both daemon and 
        normal running celery servers will be killed. This is a last 
        resort meant to clean up stray processing.

        Any process billiard command with an Image name of python.exe
        or celery.exe will be killed'''
    from vsi.windows.wmic import Pgrep
    
    pids = Pgrep(['where', "CommandLine like '%from billiard.forking import main; main()%' and Name='python.exe'"])
    pids = map(lambda x: x['processid'], pids.pids) #Get the process ids
    for pid in pids:
      self.kill(pid, force=True, tree=False, user=None)

    pids = Pgrep(['where', "CommandLine like '%celery-script%' and Name='python.exe'"])
    pids = map(lambda x: x['processid'], pids.pids) #Get the process ids
    for pid in pids:
      self.kill(pid, force=True, tree=False, user=None)
      
    super(Celeryd, self).killAllCli()
  killAllCli.name = 'killall'
  killAllCli.help = 'Kills all processes that look like a celery daemon'

if __name__=='__main__':
  Celeryd().cli()