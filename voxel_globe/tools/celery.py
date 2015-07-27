
import voxel_globe.tools.subprocessbg as subprocess
import logging
import os
import threading

STDERR_LEVEL=logging.DEBUG;
STDOUT_LEVEL=logging.DEBUG;
STDERR_PREAMBLE='stderr:'
STDOUT_PREAMBLE='stdout:'

if os.name == 'nt' and os.environ['VIP_DAEMON_BACKGROUND'] == '1':
    subprocess.STARTUPINFO.dwFlags = subprocess.STARTF_USESHOWWINDOW

class StdLog:
  def __init__(self, logger, level, preamble):
    self.logger=logger;
    self.level=level;
    self.preamble=preamble;
  def write(self, s):
    self.logger.log(self.level, self.preamble+s);

class LogPipe(threading.Thread):
  '''I don't particularly like hainv to create a pipe for this,
     But it makes sense that you need a REAL fid, since it's another
     process, and this is probably the only way to do it'''
  #http://codereview.stackexchange.com/questions/6567/how-to-redirect-a-subprocesses-output-stdout-and-stderr-to-logging-module

  def __init__(self, logger, level, preamble):
    """Setup the object with a logger and a loglevel
    and start the thread
    """
    threading.Thread.__init__(self)
    self.daemon = False
    self.logger = logger
    self.level = level
    self.preamble = preamble;
    fdRead, fdWrite = os.pipe()
    self.pipeReader = os.fdopen(fdRead, 'r')
    self.pipeWriter = os.fdopen(fdWrite, 'w')
    #self.start()
  
  def fileno(self):
    """Return the write file descriptor of the pipe
    """
    return self.pipeWriter.fileno()
  
  def run(self):
    """Run the thread, logging everything.
    """

    #This may only be NECESSARY in windows
    try: #incase SOMEONE uses the same object multiple times
      self.pipeWriter.close()
    except OSError:
      pass;

    for line in iter(self.pipeReader.readline, ''):
      if line != '\n':
        self.logger.log(self.level, self.preamble+line.strip('\n'))

    try: #incase SOMEONE uses the same object multiple times
      self.pipeReader.close()
    except OSError:
      pass;
  
  def close(self):
    """Close the write end of the pipe.
    """
    os.close(self.fdWrite)

class Popen(subprocess.Popen):
  def __init__(self, *args, **kwargs):
    self.logger = kwargs.pop('logger', None)
    self.logPipeOut = None;
    self.logPipeErr = None;

    if self.logger and 'stderr' not in kwargs:
      self.logPipeErr=LogPipe(self.logger, STDERR_LEVEL, STDERR_PREAMBLE);
      kwargs['stderr'] = self.logPipeErr;
    if self.logger and 'stdout' not in kwargs:
      self.logPipeOut=LogPipe(self.logger, STDOUT_LEVEL, STDOUT_PREAMBLE)
      kwargs['stdout'] = self.logPipeOut;

    super(Popen, self).__init__(*args, **kwargs);

    #Start the loggers (which close the parent copy of write side of the pipe
    if self.logPipeErr:
      self.logPipeErr.start()
    if self.logPipeOut:
      self.logPipeOut.start()
  
  def wait(self):
    super(Popen, self).wait()
    
    #This should guarentee the thread doens't log after the job is complete,
    #IF .wait is called...
    if self.logPipeErr:
      self.logPipeErr.join()
    if self.logPipeOut:
      self.logPipeOut.join()

# def Popen(args, logger=None, **kwargs):
#   logPipeOut = None;
#   logPipeErr = None;
#   if logger and 'stderr' not in kwargs:
#     logPipeErr=True;
#     kwargs['stderr'] = LogPipe(logger, STDERR_LEVEL, STDERR_PREAMBLE);
#   if logger and 'stdout' not in kwargs:
#     logPipeOut=True
#     kwargs['stdout'] = LogPipe(logger, STDOUT_LEVEL, STDOUT_PREAMBLE);
#   
# 
#   pid = subprocess.Popen(args, **kwargs);
# 
#   if logPipeErr:
#     kwargs['stderr'].start()
#   if logPipeOut:
#     kwargs['stdout'].start()
# 
#   return pid;
