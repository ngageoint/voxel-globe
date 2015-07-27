1>2# : ^
'''
@echo off
%~dp0sysv.bat %~f0 %*
'''

from sysv import Simple, SysVCli
from os import environ as env
import colorama

class Notebook(Simple, SysVCli):
  def __init__(self):
    self.name = 'notebook'
    self.cmd = ['ipython', 'notebook', '--no-browser',
                '--notebook-dir='+env['VIP_NOTEBOOK_RUN_DIR'],
                '--port='+env['VIP_NOTEBOOK_PORT'],
                '--ip='+env['VIP_NOTEBOOK_IP'],
                '--ipython-dir='+env['VIP_NOTEBOOK_PROFILE_DIR'],
                '--profile-dir='+env['VIP_NOTEBOOK_PROFILE_DIR']]

    self.user = env.pop('VIP_DAEMON_USER', None)

    self.registerTestCli(self.testCli)
    self.registerCli(self.killAllCli)
    
    super(Notebook, self).__init__()

  def testCli(self):
    ''' Test is notebook running
    
        Tests to see if the notebook server is running by attempting to connect
        to localhost:NOTEBOOK_PORT and downloading the main index page'''
    return self.urlTest('http://localhost:%s/' % env['VIP_NOTEBOOK_PORT'], 
                        timeout=10, ignoreHttpError=True)
                        #This will work until I get the real server registry working
  testCli.name='test'
  testCli.help='Tests if notebook is working, by downloading the index page'

  def killAllCli(self):
    ''' Kill all notebook servers

        This will attempt to kill all notebook servers running, regardless of
        how they were started. This mean both daemon and normal running 
        notebook servers will be killed. This is a last resort meant to
        clean up stray processing.

        Any process with a command line containing the word notebook and with 
        an Image name of python.exe will be killed'''
    from vsi.windows.wmic import Pgrep
    
    pids = Pgrep(['where', "CommandLine like '%notebook%' and Name='python.exe'"])
    pids = map(lambda x: x['processid'], pids.pids) #Get the process ids
    for pid in pids:
      self.kill(pid, force=True, tree=False, user=None)
  killAllCli.name = 'killall'
  killAllCli.help = 'Kills all processes that look like a notebook server'

if __name__=='__main__':
  Notebook().cli()
