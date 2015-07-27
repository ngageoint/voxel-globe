1>2# : ^
'''
@echo off
%~dp0sysv.bat %~f0 %*
'''

from sysv import SimpleDaemon, SysVCli, SysV
from os import environ as env
from posixpath import join as pathjoin
import os
import signal
from subprocess import Popen, PIPE
import time

class Rabbitmq(SimpleDaemon, SysVCli):
  def __init__(self):
    self.name = 'rabbitmq'
    self.cmd = ['rabbitmq-server.bat']
    
    self.user = env.pop('VIP_DAEMON_USER', None)
    
    self.registerCli(self.daemonCli)
    self.registerCli(self.killAllCli)
    self.registerTestCli(self.testCli)

    super(Rabbitmq, self).__init__()
  def killAllCli(self, force=False):
    ''' Kill all rabbitmq server pids

        This will attempt to kill all rabbitmq processes running, 
        regardless of how they were started. This mean both daemon and 
        normal running rabbitmq servers will be killed. This is a last 
        resort meant to clean up stray processing.

        Any process rabbitmq command with an Image name of erl.exe
        with rabbit in the commandline will be killed. epmd.exe is
        also killed'''
    from vsi.windows.wmic import Pgrep
    
    pids = Pgrep(['where', "CommandLine like '%rabbit%' and Name='erl.exe'"])
    pids = map(lambda x: x['processid'], pids.pids) #Get the process ids
    for pid in pids:
      self.kill(pid, force=True, tree=False, user=None)
    SysV.taskkill(['/im', 'epmd.exe', '/f'])
  killAllCli.name = 'killall'
  killAllCli.help = 'Kills all processes that look like a rabbitmq daemon'

  def stop(self, force=False):
    if force:
      rv = super(Rabbitmq, self).stop(force=force)
    else: #The correct gentle way 
      pid = Popen(['rabbitmqctl.bat', 'stop'], 
                  stdout=open(os.devnull, 'w'),
                  stderr=open(os.devnull, 'w'),
                  stdin=open(os.devnull, 'r'))
      rv = (pid.wait()==0, self.getPid())

    cmd = ['/IM', env['VIP_RABBITMQ_DAEMON']]
    if force:
      cmd.append('/f')
    SysV.taskkill(cmd, user=self.user)

    return rv

  def daemonCli(self):
    env['RABBITMQ_BASE']=env['VIP_PROJECT_ROOT']
    env['RABBITMQ_LOG_BASE']=env['VIP_RABBITMQ_LOG_DIR']
    env['RABBITMQ_MNESIA_BASE']=env['VIP_RABBITMQ_MNESIA_BASE']
    env['HOMEDRIVE']=env['VIP_RABBITMQ_BASE_DRIVE']
    env['HOMEPATH']=env['VIP_RABBITMQ_BASE_PATH']
    env['RABBITMQ_PID_FILE']=env['VIP_RABBITMQ_PID_FILE']
    env['ERLANG_HOME']=env['VIP_RABBITMQ_ERLANG_HOME']
    
    if not os.path.exists(env['VIP_RABBITMQ_LOG_DIR']):
      os.mkdir(env['VIP_RABBITMQ_LOG_DIR']);
    
    # print ' '.join(['pgrep.bat', '-F', 'ProcessId', '-H', 'epmd.exe'])
    # pid = Popen(['python', env['VIP_UTIL_DIR']+'/pgrep.bat', '-F', 'ProcessId', '-H', 'epmd.exe'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    # oldEpmdPids = set(map(int,pid.communicate()[0].split()))
    
    self.daemon()
    
    '''simpleWrap(['-o', pathjoin(env['VIP_RABBITMQ_LOG_DIR'], 'rabbitmq_out.log'),
                '-e', pathjoin(env['VIP_RABBITMQ_LOG_DIR'], 'rabbitmq_err.log'),
                '-p', self.getPidFile(),
                'rabbitmq-server.bat'])'''

    # pid = Popen(['python', env['VIP_UTIL_DIR']+'/pgrep.bat', '-F', 'ProcessId', '-H', 'epmd.exe'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    # newEpmdPids = set(map(int,pid.communicate()[0].split()))
    # t1 = time.time()
    # while not (newEpmdPids-oldEpmdPids) and time.time()-t1 < 10.0:
    # print oldEpmdPids, newEpmdPids
  daemonCli.name = 'daemon'
  daemonCli.help = 'This is the actual command called to start rabbitmq. You should not be calling this directly'

  def test(self):
    pid = Popen(['rabbitmqctl.bat', 'status'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    (o,e) = pid.communicate()
    return o.split('\n')[1].startswith('Error')

    
if __name__=='__main__':
  Rabbitmq().cli()