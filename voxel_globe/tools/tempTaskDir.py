
import os
from os import environ as env

from vsi.tools.dir_util import TempDir

def taskDir(cd=False):
  ''' Creates and returns a new processing directory for a celery task '''
  if not os.path.exists(env['VIP_TEMP_DIR']):
    os.makedirs(env['VIP_TEMP_DIR']);

  #make instance specific directory
  if env['VIP_CONSTANT_TEMP_DIR'] == '1':
    processing_dir = env['VIP_TEMP_DIR'];
    return TempDir(processing_dir, cd=cd, delete=False)
  else:
    return TempDir(env['VIP_TEMP_DIR'], cd=cd, delete=not env['VIP_TEMP_KEEP']=='1', mkdtemp=True)