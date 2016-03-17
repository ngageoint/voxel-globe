from __future__ import absolute_import

import logging
import os
import threading


import celery.result


import voxel_globe.tools.subprocessbg as subprocess

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
  '''I don't particularly like having to create a pipe for this,
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
    self.logPipeOut = None
    self.logPipeErr = None

    if self.logger:
      from vsi.tools.python import args_to_kwargs, command_list_to_string
      from subprocess import Popen as Popen_orig
      kwargs_view = args_to_kwargs(Popen_orig, args, kwargs)
      self.logger.debug('Popen cmd: %s' % command_list_to_string(kwargs_view['args']))

      if 'stderr' not in kwargs:
        self.logPipeErr=LogPipe(self.logger, STDERR_LEVEL, STDERR_PREAMBLE);
        kwargs['stderr'] = self.logPipeErr
      if 'stdout' not in kwargs:
        self.logPipeOut=LogPipe(self.logger, STDOUT_LEVEL, STDOUT_PREAMBLE)
        kwargs['stdout'] = self.logPipeOut

    super(Popen, self).__init__(*args, **kwargs)

    #Start the loggers (which close the parent copy of write side of the pipe
    if self.logPipeErr:
      self.logPipeErr.start()
    if self.logPipeOut:
      self.logPipeOut.start()
  
  def wait(self):
    super(Popen, self).wait()
    
    #This should guarantee the thread doesn't log after the job is complete,
    #if self.wait is called
    if self.logPipeErr:
      self.logPipeErr.join()
    if self.logPipeOut:
      self.logPipeOut.join()


def unroll_result(result):
  ''' Unroll the results from a celery task OR canvas
  
      Return Value - A list of results '''
  if isinstance(result, celery.result.AsyncResult):
    return unroll_chain_result(result)
  else:
    Exception('Can not unroll anything other than chain (AsyncResult) until '+\
              'celery 3.2 at LEAST')

def unroll_chain_result(result, children=None):
  if not children: #First recursive call has None
    children = [result] #Make a NEW list
  else:
    children.append(result)
  if result.parent: #just another child
    return unroll_chain_result(result.parent, children)
  else: #it's the final ancestor
    children.reverse()#Reverse the order since I used append instead of prepend
    return children