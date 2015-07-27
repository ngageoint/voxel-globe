#I have to rename it, because apparently import subprocess will import MYSELF
#Not anymore thanks to future ;) Oh well

''' This is a wrapper around Popen to help guarantee the calls in windows
    are indeed in the background. Use this instead of subprocess.Popen'''

#Because of celery.py
from __future__ import absolute_import

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

#Get EVERYTHING so that anything that imports this as subprocess does not 
#notice
import subprocess
tmpdfghjkiujyhgvc = subprocess.__all__
delattr(subprocess, '__all__')
from subprocess import *
subprocess.__all__ = tmpdfghjkiujyhgvc
__all__ = tmpdfghjkiujyhgvc
del tmpdfghjkiujyhgvc

Popen_original = Popen

class Popen(Popen_original):
  def __init__(self, *args, **kwargs):
    logger.debug('Popen (*%s, **%s)', args, kwargs)
    if mswindows and os.environ['VIP_DAEMON_BACKGROUND'] == '1':
      if len(args)>= 13:
        args[12].dwFlags |= STARTF_USESHOWWINDOW
      else:
        startup_info = kwargs.pop('startupinfo', STARTUPINFO())
        STARTUPINFO.dwFlags |= STARTF_USESHOWWINDOW
        kwargs['startupinfo'] = startup_info
    return super(Popen, self).__init__(*args, **kwargs)

if __name__=='__main__':
  import sys
  pid = Popen(sys.argv[1:])