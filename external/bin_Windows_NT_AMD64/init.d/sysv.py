#!/dfsd

''' A python module to give SYSV init.d functionality. Hopefully, it is better
    in many ways. simple.py contains a simply '''

from os import environ as env
from subprocess import PIPE, STDOUT, STARTUPINFO, STARTF_USESHOWWINDOW
from subprocess import Popen as Popen_orig
from os.path import join as pathjoin
import os
import signal
import time
import textwrap
import argparse
import sys

import colorama

from vsi.console import getTerminalSize

''' You need elevated permissions for other user 
    This needs to called by the VIP environment''' 

def Popen(*args, **kwargs):
  '''helper'''
  if env['VIP_DAEMON_BACKGROUND'] == '1':
    STARTUPINFO.dwFlags = STARTF_USESHOWWINDOW
  return Popen_orig(*args, **kwargs)

class SysVException(Exception):
  ''' Exceptions throw by SysV '''
  pass

class SysV(object):
  ''' Python implmentation for SysV init.d functionality

      This is an abstract class for SysV init.d, to use it, you must define name, and cmd
      
      class MyDaemon(SysV):
        def __init__(self):
          self.name = 'mydaemon'
          self.cmd = ['daemon.exe', '-c', 'someoption.conf']
          super(MyDaemon, self).__init__()
      '''
  def __init__(self):
    if self.name is None:
      raise SysVException('name must not be None')
    if self.cmd is None:
      raise SysVException('cmd must not be None')

    if not hasattr(self, 'user'):
      self.user = None

    if not hasattr(self, 'precmd'):
      self.precmd = []

    #I purposefully do not store pid in the class, in case it changes on disk
    
    super(SysV, self).__init__()
    
  def getPidFile(self):
    ''' Get the pid filename
    
        Returns a pid filename for the daemon (uses environment var VIP_INIT_DIR)'''
    return os.path.join(env['VIP_INIT_DIR'], self.name+'.pid')

  def removePidFile(self):
    ''' Deletes the pid filename
    
        Deletes self.getPidFile(), to denote the daemon is down
        This is down by self.waitStop upon success'''
    pidFile = self.getPidFile()
    if os.path.exists(pidFile):
      os.remove(pidFile)
    
  def getPid(self):
    ''' Get the pid (usually read from pid file)
    
        Reads the pid # from self.getPidFile()'''
    try:
      with open(self.getPidFile(), 'r') as fid:
        return int(fid.read())
    except:
      return -1
      
  def setPid(self, pid):
    ''' Save the pid (usually to the pid file)
    
        Write the pid number to self.getPidFile()
        
        Arguments:
        pid - pid number'''
    with open(self.getPidFile(), 'w') as fid:
      fid.write('%d' % pid)
      fid.close() #Flush NOW
  
  def start(self, alternativeCommand=None):
    ''' Starts daemon as self.user
    
        Starts the daemon (self.cmd) as self.user. If no self.user is None. 
        Then self.cmd is executed. If there is a self.user, then psexec is 
        used to run wrap.bat in the background (if environment variable 
        VIP_DAEMON_BACKGROUND is set to "1")
        
        Optional argument:
        alternativeCommand
        
        Returns (was_cmd_executed, pid)
        was_cmd_executed is only false if the daemon is already running'''
    
    if alternativeCommand is not None:
      cmd = alternativeCommand
    else:
      cmd = self.precmd+self.cmd
    
    status = self.status()
    if status[0]:
      return (False, status[1])
#    stdout = getattr(self, 'stdout', None)
#    stderr = getattr(self, 'stderr', None)

    if self.user is not None:
      #When you change users, you lose the environment, so we need to call wrap again
      precmd =  ['psexec', '-accepteula', '-u', self.user, '-d', '-i']
      if env['VIP_DAEMON_BACKGROUND'] == '1':
        precmd += [os.path.join(env['VIP_PYTHON_DIR'], 'pythonw'),
                   os.path.join(env['VIP_INIT_DIR'], 'bg.py')]
      precmd += [os.path.join(env['VIP_PROJECT_ROOT'],'wrap.bat')]

      if env['VIP_DAEMON_BACKGROUND'] == '1':
        pid = Popen(precmd+cmd, stdout=open(os.devnull, 'w'), stderr=STDOUT, stdin=open(os.devnull, 'r'))
      else:
        pid = Popen(precmd+cmd)
      #[o,e] = pid.communicate() #bleed psexec stdout
      #if not env['VIP_DAEMON_BACKGROUND'] == '1':
      #  print o, e
      #pid.wait() #psexec with -d launches and ends
      pid = pid.pid #Technically the wrong pid!
    else:
      '''if stdout is not None:
        stdout = open(stdout, 'w')
      if stderr is not None:
        if stderr == stdout.name:
          stderr = STDOUT
        else:
          stderr = open(stderr, 'w')'''

      #Make the running program hidden (default is 0 which is hidden)

      pid = Popen(self.precmd+self.cmd)#, stdout=stdout, stderr=stderr)
      pid = pid.pid
      #self.setPid(pid)
    return (True, pid)

  def stop(self, force=False, tree=False):
    ''' Stops the daemon
    
        Kills the daemon pid using kill(taskkill).
        
        Optional arguments:
        force - bool to use force kill or not (default: False)
        tree - bool to send kill to ancestors of pid or not (default: True)
        
        Returns (was_the_pid_running, pid) '''
    (status, pid) = self.status()
    if status:
      SysV.kill(pid, user=self.user, force=force, tree=tree)
      return (True, pid)
    else:
      return (False, pid)

  def waitStart(self, timeout=2.0, interval=0.1):
    ''' Waits for the daemon to stop
    
        Uses test if available, else it just waits for the main pid to disappear
        
        Returns 0 on confirmation daemon is working, else 1 if timeout exceeded'''
    t1 = time.time()
    while time.time()-t1<timeout:
      if 'test' in self.clis:
        if self.clis['test']() == 0:
          return 0
      elif self.status()[0]: #if is running
        return 0
      time.sleep(interval)
    return 1

  def waitStop(self, timeout=2.0, interval=0.1):
    ''' Waits for the daemon to stop
    
        Uses test if available, else it just waits for the main pid to disappear,
        and then removes the pid file when it does
        
        Returns 0 on confirmation daemon is dead, else 1 if timeout exceeded'''
    t1 = time.time()
    while time.time()-t1<timeout:
      if 'test' in self.clis:
        #Wait for test to fail and for pid to stop
        if self.clis['test']() != 0 and not self.status()[0]:
          self.removePidFile()
          return 0
      elif not self.status()[0]:
      #If no test is available, just use is the pid running
        self.removePidFile()
        return 0
      time.sleep(interval)
    return 1
      
  # def wait(self, timeout=20.0, pid=None, interval=0.25 ):
    # ''' Waits timeout seconds for pid to finish (in interval intervals) '''
    # if pid is None:
      # pid = self.getPid()
    
    # t1 = time.time()
    # while time.time()-t1 < timeout:
      # if not SysV.isRunning(pid):
        # self.removePidFile()
        # return True
      # time.sleep(interval)
    # return not SysV.isRunning(pid)

  def restart(self, timeout=20):
    ''' Restarts the daemon (Deprecated??)
    
        Stops daemon, waits up to timeout seconds for the pid to die, and then
        starts the daemon if the timeout was not exceeded

        Optional arguments:
        timeout - float seconds (default: 20)
        
        Returns ((killed, originalPid), (was_cmd_executed, pid))'''
    status = self.stop()
    if self.waitStop(timeout):
      return (status, self.start())
    else:
      return (status,)

  def status(self):
    ''' Get Status of this daemon.
    
        Returns (boolean is running, pid#)'''
    pid = self.getPid()
    return (SysV.isRunning(pid), pid)
  
  @staticmethod
  def isRunning(pid):
    ''' Returns if the pid is running
    
        Simply checks if the pid # is running via tasklist
        (There's always a rare chance the daemon died, 
         and this is a different process)'''
    if pid < 1:
      return False
    pid = Popen(['tasklist', '/fi', 'pid eq %d' % pid, '/fo:csv'], stdout=PIPE, stderr=PIPE)
    (o,e) = pid.communicate()
    if not env['VIP_DAEMON_BACKGROUND'] == '1':
      print o, e
    if o.startswith('INFO: No tasks'):
      return False

    ''' If I ever choose to verify the pid commandline matches (what I would put in the pid file
        Here would be a good place. This is useful in case the daemon is really dead, but some
        other random process is running useing that pid. I would also need to rewrite setPid to
        call "pgrep -p {myPid} -H -F commandline" and save that in the pid file too. Then I would
        have to update daemons like httpd that save thier own pid file, and still save my own (in
        addition to a different file they use).''' 
    return True
      
  ''' os.kill in windows is JUST A BAD IDEA!
  @staticmethod
  def kill(pid, signal=signal.SIGTERM, user=None):
    if user is None:
      os.kill(pid, signal)
    else:
      pid = Popen(['psexec', '-accepteula', '-u', user,
                   os.path.join(env['VIP_PYTHON_DIR'], 'python.exe'), 
                   '-c', 'import os; os.kill(%d, %d)' % (pid, signal)],
                  stdout=PIPE, stderr=PIPE)
      pid.communicate()#bleed stdout
      pid.wait()'''

  @staticmethod
  def kill(pid, force=False, tree=True, user=None):
    ''' Uses SysV.taskkill to kill a pid
    
        Argument:
        pid - pid number
        Optional Arguments:
        force - Force kill or not (default: False)
        tree - Send kill signal to tree of pids or not (default: True)
        user - User to send kill as (default: use self)
               You probably need elevated permissions to be able to
               use this (unless user=None)'''
    tree = tree or force
    args = ['/pid', str(pid)]
    if force:
      args += ['/F']
    if tree:
      args += ['/T']
    SysV.taskkill(args, user)

  @staticmethod
  def taskkill(args, user=None):
    ''' Silently runs taskkill (as user if specified)
    
        Uses Windows' taskkill to kill a process. This is better than using
        os.kill, because it will successfully kill an entire tree of pids.
        os.kill will only kill the main pid, and leave the rest running. This
        is useless in cases where ipython.exe really spawns 
        'python ipython-script.py' and killing ipython is just a dummy. I'm
        not sure how taskkill works, because it has a /t option for killing
        a tree, and without /t, it still successfully kills everything''' 
    cmd = []

    if user is not None:
      cmd += ['psexec', '-accepteula', '-u', user, '-i']

    if env['VIP_DAEMON_BACKGROUND'] == '1':
      cmd += [os.path.join(env['VIP_PYTHON_DIR'], 'pythonw'),
              os.path.join(env['VIP_INIT_DIR'], 'bg.py')]
    # else:
      # cmd += [os.path.join(env['VIP_PYTHON_DIR'], 'python'), '-c',
              # 'import sys as s; from subprocess import Popen; print s.argv[1:]; Popen(s.argv[1:]); raw_input()']

    cmd += ['taskkill']
    if env['VIP_DAEMON_BACKGROUND'] == '1':
      pid = Popen(cmd + args, stdout=open(os.devnull, 'w'), stderr=STDOUT, stdin=open(os.devnull, 'r'))
    else:
      pid = Popen(cmd + args)
    #o,e = pid.communicate()#bleed stdout
    #if not env['VIP_DAEMON_BACKGROUND'] == '1':
    #  print o, e
    #pid.wait()


class SysVCli(object):
  ''' All of the CLI interfaces for the SysV class
  
      This should inherited with SysV
      
      class MyDaemon(SysV, SysVCli):
        pass #Stuff''' 
  def __init__(self):
    #In case inherited class override this first
    self.registerCli(self.startCli, False)
    self.registerCli(self.stopCli, False)
    self.registerCli(self.killAllCli, False)
    self.registerCli(self.restartCli, False)
    self.registerCli(self.condrestartCli, False)
    self.registerCli(self.statusCli, False)
    self.registerCli(self.helpCli, False)
    
    super(SysVCli, self).__init__()
    
  def registerCli(self, cmd, overwrite=True, name=None):
    ''' Register a function with the CLI 
    
        All CLI function should return a single number, to be used as the exit
        value. 0 mean no problem, anything else is an error/warning
        
        Optionally (but recommended), every function should the following two attributes
            .name - the name of the cli command. If this is not supplied, then the name
                    of the function in python is used
            .help - Short help string to explain the command in help
        You should also include a docstring help section too, to contain more detailed
        help, use case/scenario, and arguments'''
    #In case it doesn't exist yet
    if not hasattr(self, 'clis'):
      self.clis = {}
    if name is None:
      name = getattr(cmd, 'name', cmd.__name__)

    if overwrite==False and name in self.clis:
      return

    self.clis[name] = cmd

  def cli(self):
    ''' The main CLI interface called.
    
        Simply call this from your main function
        
        if __name__=='__main__':
          MyDaemon().cli() '''
          
    if hasattr(sys.stdout, 'close') and hasattr(sys.stderr, 'close'):
      colorama.init()
    parser = argparse.ArgumentParser(epilog='Try the "help" command for SYSV help');
    parser.add_argument('command', nargs=1, help='Use the help command to list all SYSV commands. Typically start, stop, restart, status, etc...')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command + args.args
  
    ''' Implement basic CLI '''
    if command[0] in self.clis:
      rv = self.clis[command[0]](*command[1:])
    else:
      rv = self.otherCli(command)
    
    exit(rv)
      
  def otherCli(self, command):
    ''' Easy way to add override '''
    raise SysVException('Unknown command')

  def startCli(self):
    ''' Starts the daemon 

        Returns 0 on successfully executing start command, else 1
        (Note: This does not guarantee the start command executed 
         successfully, just that it was successfully execute, in
         other words the command existed, but may have failed still
         This is why a test is so important)'''
    (started, pid) = self.start()
    if started:
      print 'Starting %s (%d)' % (self.name, pid)
      return 0
    print '%s (%d) was already running' % (self.name, pid)
    return 1
  startCli.help = 'Starts the daemon'
  startCli.name = 'start'
  
  def stopCli(self, force=False):
    ''' Stops the daemon
    
        Sends a kill signal to the main pid and tree
        
        Takes one optional argument
        force - /f means force kill, else normal kill signal

        Returns 0 if kill signal is sent, or 1 if no signal sent '''
    if type(force) == str:
      force = force.lower()=='/f'

    (killed, pid) = self.stop(force=force)
    if killed:
      if force:
        print 'Forced',
      print 'Kill signal sent to %d' % pid
      return 0
    else:
      print 'No kill signal sent to %d, it wasn\'t running' % pid
      return 1
  stopCli.help = 'Send the kill command to the pid of the daemon'
  stopCli.name = 'stop'

  def killAllCli(self):
    ''' Kill all processes that look like the first command argument.exe

        This will attempt to kill all processes running that appear to
        be the server, regardless of how they were started. This mean 
        both daemon and normal running processes with the same image name
        will be killed. This is a last resort meant to clean up stray 
        processing.

        This should probably be redefined for all but the most basic of 
        cases'''
    imageName = self.cmd[0]
    if '.' not in imageName:
      imageName = imageName + '.exe'
    SysV.taskkill(['/im', imageName, '/f'])
  killAllCli.name = 'killall'
  killAllCli.help = 'Kills all processes that look like a postgres'
  
  def restartCli(self, timeout=20):
    ''' Restart the daemon
    
        Stops the daemon, and after waiting up to the timeout for it to daemon to stop,
        start the daemon again, unconditionally
        
        Takes one optional argument
        timeout - float, default 20
        
        Returns 0 if start executed, 1 if not'''
    timeout = float(timeout)
    
    self.clis['stop']()
    self.waitStop(timeout=20, interval=0.1)
    return self.clis['start']()
  restartCli.help = 'Restarts the daemon. Stops it, wait up to 20 second for the dameon to die, and then starts it again'
  restartCli.name = 'restart'

  def condrestartCli(self, timeout=20.0):
    ''' Conditional restart the daemon
    
        Stops the daemon, and after waiting the timeout for it to daemon to stop,
        if it successfully stops, start the daemon again
        
        Takes one optional argument
        timeout - float, default 20
        
        Returns 0 if start executed, 1 if not'''
    timeout = float(timeout)

    self.clis['stop']()
    if self.waitStop(20, interval=0.1):
      return self.clis['start']()
    return 1
  condrestartCli.help = 'Conditionally restarts the daemon. Stops it, wait up to 20 second for the dameon to die. Only if the daemon pid is gone, will it then start it again'
  condrestartCli.name = 'condrestart'

  def statusCli(self):
    ''' Prints if the main pid is running or not 

        Returns 0 if running, 1 if not'''
    (running, pid) = self.status()
    if running:
      print colorama.Fore.GREEN+'%-16s (%5d) is running' % (self.name, pid), colorama.Fore.RESET
      return 0
    if pid == -1:
      print colorama.Fore.RED+'%-16s is not running' % (self.name), colorama.Fore.RESET
    else:
      print colorama.Fore.YELLOW+'%-16s (%5d) appears to be dead' % (self.name, pid), colorama.Fore.RESET
    return 1
  statusCli.help = 'Prints out the status of the daemon pid'
  statusCli.name = 'status'

  def helpCli(self, command=None):
    ''' Prints helpful information

        help - list all register CLI command
        help [command] - prints the docstring help for that command'''
    if command and command in self.clis:
      import pydoc
      pydoc.help(self.clis[command])
      #Why does this not work? help(self.clis[command])
    else:
      print 'Usage: %s [command]\n' % os.path.split(sys.argv[0])[-1]
      print 'Supported commands:'
      commandWidth = max(map(len, self.clis.keys()))
      commandWidth = min(commandWidth, 20) #20 is the most I'm willing to sacrifice
      for cli in self.clis:
        help = getattr(self.clis[cli], 'help', 'No help provided')
        print textwrap.fill(('{:<%d} - {}' % commandWidth).format(cli, help), width=getTerminalSize()[0]-1, subsequent_indent=' '*(commandWidth+3))
      print '\nFor docstring on a particular command'
      print '\t%s help [command]' % os.path.split(sys.argv[0])[-1]
      return 0
  helpCli.help = 'Print the help for all registered commands'
  helpCli.name = 'help'
  
  ''' These are place holders for the test '''

  def registerTestCli(self, testCli=None):
    ''' Helper fun to register the test CLI, and wait start/wait stop 
    
        Optional argument:
        testCli - The function to be registered for the test function.
                  The test function must either be named test, or have
                  .name === 'test\''''
    if testCli is None:
      testCli = self.testCli
    assert(testCli.name == 'test' or testCli.__name__ == 'test')
    self.registerCli(testCli)
    self.registerCli(self.waitStartCli)
    self.registerCli(self.waitStopCli)

  def testCli(self):
    ''' A little more in depth than status, meant to check "Is the daemon up
        and loaded and working now, usually, accepting connections?" 
        
        You need to have a self.test function that takes only self an an 
        argument, and returns 0 for success, and not zero for failure (1)
        
        Register a the test CLI with:
        >>> self.registerTestCli() 
        And this will register the testCli, waitStartCli, and waitStopCli'''
    rv = self.test()
    if rv==0:
      print colorama.Fore.GREEN+'%-16s is running and accepting connections' % self.__class__.__name__, colorama.Fore.RESET
    else:
      if self.status()[0]:
        print colorama.Fore.YELLOW+'%-16s is not accepting connections' % self.__class__.__name__, colorama.Fore.RESET
      else:
        print colorama.Fore.RED+'%-16s is not running' % self.__class__.__name__, colorama.Fore.RESET
    return rv
  testCli.name='test'
  testCli.help='Tests if daemon is working, by calling the test method'

  def urlTest(self, url, timeout=10, ignoreHttpError=False):
    ''' Test if a url will download
    
        This is a common way of testing a daemon, yet it is still less than 
        straight forward. This is a helper function to do all those details
        for you. This is not a CLI, but can be called by the testCli.
        
        Parameter:
        url - The url you want to download successfully to deem the daemon
              is running.
        
        Optional Parameters:
        timeout - Max time to wait to connect, in seconds. Default - 10
        ignoreHttpErrors - If true, than HTTP Errors like Error 500, etc
                           return success, else they return failure

        Return value - 0 means success, >0 is a failure'''

    import urllib2
    import socket

    try:
      urllib2.urlopen(url, timeout=timeout)
    except urllib2.HTTPError as e:
      #I know the server is running here
      print colorama.Fore.YELLOW+'%-16s is running and accepting connections, but...' % self.__class__.__name__
      print 'HTTP %d Error:' % e.getcode(), str(e.reason)+colorama.Fore.RESET
      print 'Another daemon is probably not running or configuration error'
      if ignoreHttpError:
        return 0
      else:
        return 2 #Just return, no need to check if server is running
    except urllib2.URLError:
      rv = 1
    except socket.error:
      print colorama.Fore.RED+'The %s server just disconnected' % self.__class__.__name__, colorama.Fore.RESET
      rv = 3
    except Exception as e:
      print colorama.Style.BRIGHT+colorama.Fore.MAGENTA+'Unknown exception on %s.' % self.__class__.__name__, str(e), colorama.Style.NORMAL+colorama.Fore.RESET
      rv = 999
    else:
      print colorama.Fore.GREEN+'%-16s is running and accepting connections' % self.__class__.__name__, colorama.Fore.RESET
      return 0

    #A little more verbose as to why there may have been failes    
    if self.status()[0]:
      print colorama.Fore.YELLOW+'%-16s is not accepting connections' % self.__class__.__name__, colorama.Fore.RESET
    else:
      print colorama.Fore.RED+'%-16s is not running' % self.__class__.__name__, colorama.Fore.RESET

    return rv

  def waitStartCli(self, timeout=5.0):
    ''' Takes one cli argument, 
        timeout - float'''
    timeout = float(timeout)
    return self.waitStart(timeout=timeout)
  waitStartCli.name = 'waitstart'
  waitStartCli.help = 'Waits for the test to succeed, and then returns. Useful to knowing the daemon is truely up'

  def waitStopCli(self, timeout=5.0):
    ''' Takes one cli argument, 
        timeout - float'''
    timeout = float(timeout)
    return self.waitStop(timeout=timeout)
  waitStopCli.name = 'waitstop'
  waitStopCli.help = 'Waits for the test to fail and pid to end, and then returns. Useful to knowing the daemon is truely down'

class Simple(SysV):
  ''' This implementation is for simple executables where the cmd given
      is the pid, stdout, and stderr to be monitored, using itself as a 
      CLI. Call the super AFTER you define self.cmd and self.name'''

  def __init__(self):
    if env['VIP_DAEMON_BACKGROUND'] == '1':
      self.precmd = ['pythonw']
    else:
      self.precmd = ['python']
    self.precmd += [__file__,
                    '-p', self.getPidFile(),
                    '-o', os.path.join(env['VIP_LOG_DIR'], self.name+'_out.log'),
                    '-e', os.path.join(env['VIP_LOG_DIR'], self.name+'_err.log')]
    super(Simple, self).__init__()

class SimpleDaemon(SysV):
  ''' This implementation is for less simple executables where python has to
      be run to set up the environment before the real command is run. This
      is done using a daemon CLI. The command called by the daemon fucntion
      is the pid, stdout, and stderr to be monitored. Call the super AFTER 
      you define self.cmd and self.name'''

  def __init__(self):
    ''' Special case of SysV where a daemon function needs to be run to setup
        the environment or other as the daemon user. A daemon CLI needs to be
        define, and should call self.daemon to run the daemon command'''
    if env['VIP_DAEMON_BACKGROUND'] == '1':
      self.precmd = ['pythonw']
    else:
      self.precmd = ['python']
    self.precmd += [__file__,
                    '-p', self.getPidFile(),
                    '-o', os.path.join(env['VIP_LOG_DIR'], self.name+'_out.log'),
                    '-e', os.path.join(env['VIP_LOG_DIR'], self.name+'_err.log')]
    super(SimpleDaemon, self).__init__()

  def start(self):
    return super(SimpleDaemon, self).start(alternativeCommand= [
              os.path.join(env['VIP_PYTHON_DIR'], 'python'), 
              os.path.join(env['VIP_INIT_DIR'], '%s.bat' % self.name), 
                                 #This is a little weak here... /|\
              'daemon'])         #                               |
  
  def daemon(self, logStdout=True, logStderr=True, logPidfile=True):
    ''' The actual call to execute the dameon. When running as another user,
        This calls the actual executables
        
        Optional arguments:
        logStdout - True or False to enable or disable the logging of stdout.
                    Can also be a string to specify a different log file.
                    Does not create directory if it does not exist. 
                    Default: True
        logStderr - True or False to enable or disable the logging of stderr.
                    Can also be a string to specify a different log file.
                    Does not create directory if it does not exist. 
                    Default: True
        logPidfile - True or False to enable or disable the logging of pid file.
                     Can also be a string to specify a different log file.
                     Does not create directory if it does not exist. 
                     Default: True
                     
        Returns - Pid number'''
    args = []
    if logStdout:
      if logStdout is True:
        logStdout = pathjoin(env['VIP_LOG_DIR'], '%s_out.log' % self.name)
      args.extend(['-o', logStdout])
    if logStderr:
      if logStderr is True:
        logStderr = pathjoin(env['VIP_LOG_DIR'], '%s_err.log' % self.name)
      args.extend(['-e', logStderr])
    if logPidfile:
      if logPidfile is True:
        logPidfile = self.getPidFile()
      args.extend(['-p', logPidfile])
    return simpleWrap(args + self.precmd + self.cmd)
    
def simpleWrap(args=None):
  ''' CLI wrapper to run a command (in the background if environment 
      VIP_DAEMON_BACKGROUND is 1), and reroute stdout, stderr, stdin,
      and save pid to a pidfile. This is useful for basic daemons.
      
      Returns - Pid number'''

  description = ''' This script if for running daemons in Windows. Since there is no 
                    easy way to run a console application in the background (with no
                    console showing), this script will facilitate that '''

  parser = argparse.ArgumentParser(usage=None, description=description)
  parser.add_argument('-o', '--daemonstdout', dest='stdout', default=None, help='Filename to write stdout to')
  parser.add_argument('-e', '--daemonstderr', dest='stderr', default=None, help='Filename to write stderr to')
  parser.add_argument('-i', '--daemonstdin', dest='stdin', default=None, help='Filename to read stdin from')
  parser.add_argument('-p', '--daemonpid', dest='pidfile', default=None, help='Name of the pid file')
  parser.add_argument('command', nargs=1, help='Command to execute')
  parser.add_argument('arguments', nargs=argparse.REMAINDER, help='All other arguments for the command to be executed')
  args = parser.parse_args(args)
  
  stdin = args.stdin
  stdout = args.stdout
  stderr = args.stderr
  pidfile = args.pidfile
  
  #If stdout is specified
  if stdout is not None:
    stdout = open(stdout, 'w'); #Make it a file object
  #else its none, and unless this is meant to run in the background
  elif env['VIP_DAEMON_BACKGROUND'] == '1':
    stdout = open(os.devnull, 'w') # it should go to devnull
    
  #If stderr is specified
  if stderr is not None:
    if args.stdout==stderr: #If they were the same
    #(This isn't very robust, ././ != ./, etc...)
      stderr = STDOUT;      #tell Popen to use the same fid
    else:#else, open a new file object for err
      stderr = open(stderr, 'w');
  #else its none, and unless this is meant to run in the background
  elif env['VIP_DAEMON_BACKGROUND'] == '1':
    stderr = open(os.devnull, 'w') # it should go to devnull

  #stdin must be not None if stdout/stderr is used due to bug https://bugs.python.org/issue1124861
  if stdin is None:
    stdin = open(os.devnull, 'r')#Bogus Null stdin to keep pid running
  else:
    stdin = open(stdin, 'rb') #Make it a file object

#Debugging
#    with open(r'd:\vip\bg.txt', 'w') as fid:
#      print >>fid, stdout
#      print >>fid, stderr
#      print >>fid, stdin
#    print args.cmd
#    print os.environ['PATH']
  pid = Popen([args.command]+args.arguments, stdout=stdout, stderr=stderr, stdin=stdin)

  if pidfile is not None:
    with open(pidfile, 'w') as fid:
      fid.write('%d' % pid.pid)
  return pid.pid

if __name__=='__main__':
  simpleWrap()