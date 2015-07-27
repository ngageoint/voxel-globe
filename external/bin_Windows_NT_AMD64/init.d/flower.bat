1>2# : ^
'''
@echo off
%~dp0sysv.bat %~f0 %*
'''

from sysv import Simple, SysVCli
from os import environ as env
import colorama

class Flower(Simple, SysVCli):
  def __init__(self):
    self.name = 'flower'
    self.cmd = ['flower', '--address=0.0.0.0', '--port=%s'%env['VIP_FLOWER_PORT']]
    self.user = env.pop('VIP_DAEMON_USER', None)

    self.registerTestCli(self.testCli)
    
    self.registerCli(self.killAllCli)
    
    super(Flower, self).__init__()

  def testCli(self):
    return self.urlTest('http://localhost:%s/' % env['VIP_FLOWER_PORT'], 
                        timeout=10, ignoreHttpError=True)
                        #This will work until I get the real server registry working
  testCli.name='test'
  testCli.help='Tests if flower is working, by downloading the index page'
  
  def killAllCli(self):
    ''' Kill all flower serverS

        This will attempt to kill all flower processes running, 
        regardless of how they were started. This mean both daemon and 
        normal running flower servers will be killed. This is a last 
        resort meant to clean up stray processing.

        Any process flower command with an Image name of python.exe
        will be killed'''
    from vsi.windows.wmic import Pgrep
    
    pids = Pgrep(['where', "CommandLine like '%flower-script%' and Name='python.exe'"])
    pids = map(lambda x: x['processid'], pids.pids) #Get the process ids
    for pid in pids:
      self.kill(pid, force=True, tree=False, user=None)
    super(Flower, self).killAllCli()
  killAllCli.name = 'killall'
  killAllCli.help = 'Kills all processes that look like a flower server'

if __name__=='__main__':
  Flower().cli()