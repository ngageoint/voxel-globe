import os
from os import environ as env

from vsi.tools.dir_util import TempDir, checksum_dir

def task_dir(subdir='tmp', cd=False):
  ''' Creates and returns a new processing directory for a celery task '''
  if not os.path.exists(env['VIP_TEMP_DIR']):
    os.makedirs(env['VIP_TEMP_DIR'])

  #make instance specific directory
  if env['VIP_CONSTANT_TEMP_DIR'] == '1':
    processing_dir = os.path.join(env['VIP_TEMP_DIR'], subdir)
    return TempDir(processing_dir, cd=cd, delete=False)
  else:
    return TempDir(os.path.join(env['VIP_TEMP_DIR'], subdir), cd=cd, 
                   delete=not env['VIP_TEMP_KEEP']=='1', mkdtemp=True)

def storage_dir(subdir='tmp', cd=False):
  ''' Creates and returns a new storage directory for a celery task '''

  if not os.path.exists(env['VIP_STORAGE_DIR']):
    os.makedirs(env['VIP_STORAGE_DIR'])

  return TempDir(os.path.join(env['VIP_STORAGE_DIR'], subdir), cd=cd, 
                 delete=False, mkdtemp=True)

def image_dir(subdir='tmp', cd=False):
  if not os.path.exists(env['VIP_IMAGE_SERVER_ROOT']):
    os.makedirs(env['VIP_IMAGE_SERVER_ROOT'])

  return TempDir(os.path.join(env['VIP_IMAGE_SERVER_ROOT'], subdir), cd=cd, 
                 delete=False, mkdtemp=True)

def image_sha_dir(checksum, cd=False):
  if not os.path.exists(env['VIP_IMAGE_SERVER_ROOT']):
    os.makedirs(env['VIP_IMAGE_SERVER_ROOT'])

  return TempDir(get_image_sha_dir(checksum),
                 cd=cd, mkdtemp=False, delete=False)

def get_image_sha_dir(checksum):
  ''' Generate checksum directory name'''
  return checksum_dir(checksum, int(env['VIP_CHECKSUM_DEPTH']), 
                      base_dir=env['VIP_IMAGE_SERVER_ROOT'])
