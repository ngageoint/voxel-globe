from subprocess import Popen, STARTUPINFO, STARTF_USESHOWWINDOW, PIPE
import sys
import os

if __name__=='__main__':
  STARTUPINFO.dwFlags = STARTF_USESHOWWINDOW #Make the running program hidden
  pid = Popen(sys.argv[1:])
  
