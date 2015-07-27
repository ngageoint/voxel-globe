1>2# : ^
'''
@echo off
%~dp0sysv.bat %~f0 %*
'''

from sysv import SimpleDaemon, SysVCli, simpleWrap
from os import environ as env
import os
from os.path import join as pathjoin
import os.path
import colorama

class Httpd(SimpleDaemon, SysVCli):
  def __init__(self):
    self.name = 'httpd'

    http_options = []
    if env['VIP_HTTPD_DEBUG_INDEXES'] == "1":
      http_options.append('-Ddebug_indexes')

    self.cmd = ['httpd'] + http_options + ['-f', env['VIP_HTTPD_CONF']]

    self.user = env.pop('VIP_DAEMON_USER', None)

    self.registerTestCli(self.testCli)
    self.registerCli(self.daemonCli);

    super(Httpd, self).__init__()

  def stopCli(self, force=True):
    ''' Stops the daemon
    
        Sends a kill signal to the main pid and tree
        
        Takes one optional argument
        force - /g means graceful kill, else force kill signal by default
                This is special behaviour for httpd

        Returns 0 if kill signal is sent, or 1 if no signal sent '''
    if type(force) == str:
      force = not force.lower()=='/g'

    return super(Httpd, self).stopCli(force=force)
  stopCli.name = 'stop'
  stopCli.help = SysVCli.stopCli.help

  def testCli(self):
    return self.urlTest('http://localhost:%s/' % env['VIP_HTTPD_PORT'], 
                        timeout=10, ignoreHttpError=True)
                        #This will work until I get the real server registry working
  testCli.name='test'
  testCli.help='Tests if httpd is working, by downloading the index page'
  
  def daemonCli(self):
    ''' Creates the daemon environment and runs the command
  
      This should only be called by the start CLI. You should not be calling
      this (except maybe for debugging purposes)'''
    env['PIDFILE']=pathjoin(env['VIP_INIT_DIR'], 'httpd.pid')
    if env['VIP_HTTPD_DEPLOY_ON_START'] == "1":
      simpleWrap(['-o', pathjoin(env['VIP_HTTPD_LOG_DIR'], 'deploy_out.log'),
                  '-e', pathjoin(env['VIP_HTTPD_LOG_DIR'], 'deploy_err.log'),
                  pathjoin(env['VIP_DJANGO_PROJECT'], 'deploy.bat')])

    if not os.path.exists(env['VIP_HTTPD_LOG_DIR']):
      os.mkdir(env['VIP_HTTPD_LOG_DIR']);
    
    return self.daemon(logPidfile=False)

  daemonCli.name = 'daemon'
  daemonCli.help = 'This is the actual command called to start httpd. You should not be calling this directly'

if __name__=='__main__':
  Httpd().cli()