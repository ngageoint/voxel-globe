#!/usr/bin/env python

import os
from os import environ as env
from os.path import join as path_join
from distutils.dir_util import mkpath, copy_tree
from distutils.file_util import copy_file
import subprocess
from glob import glob
import argparse

from distutils.spawn import find_executable as which

class Rsync(object):
  def __init__(self, cmd=None):
    if cmd:
      self.exe = cmd
    else:
      self.exe = which('rsync')

  def sync(self, srcs, dest):
    ''' srcs - list of sources, dest - destination '''
    escaped_srcs = []
    for src in srcs:
      escaped_srcs.append(src.replace(' ', '\ '))

    escaped_dest = dest.replace(' ', '\ ')

    cmd = [self.exe, '-rav']
    cmd = ' '.join(cmd + escaped_srcs + [escaped_dest])

    return subprocess.Popen(cmd, shell=True)

def get_parser():
  parser = argparse.ArgumentParser(
    description="Pacakge/install vxl")
  parser.add_argument('--skip_bin', default=False, action='store_true',
    help='Skip bin directory')
  return parser

def main():

  args = get_parser().parse_args()

  windows = os.name == 'nt'
  if windows:
    exeExtention = '.exe'
    pydExtention = '.pyd'
    rsync = None
  else:
    exeExtention = ''
    pydExtention = '.so'
    rsync = which('rsync')
    if rsync:
      rsync = Rsync(rsync)
    pids = []
  
  zipDir = env['VIP_INSTALL_DIR']
  if windows:
    zipDir = path_join(zipDir, 'vxl')
    #Cause that's how its done in windows... :(

  vxlBinDir = env['VIP_VXL_BUILD_BIN_DIR']
  vxlLibDir = env['VIP_VXL_BUILD_LIB_DIR']
  
  zipBinDir = path_join(zipDir, 'bin')
  zipRoamDir = path_join(zipDir, 'roam')
  zipPythonDir = path_join(zipDir, 'lib', 'python2.7', 'site-packages', 'vxl')
  zipShareDir = path_join(zipDir, 'share', 'vxl')
  zipClDir = path_join(zipShareDir, 'cl')

  pyscript_dirs = ['contrib/brl/bseg/boxm2/pyscripts',
                   'contrib/brl/bseg/boxm2_multi/pyscripts',
                   'contrib/brl/bseg/bstm/pyscripts',
                   'contrib/brl/bseg/bvxm/pyscripts']
  pyscript_dirs = map(lambda x: path_join(env['VIP_VXL_SRC_DIR'], x),
                      pyscript_dirs)

  cl_dirs = ['contrib/brl/bseg/boxm2/ocl/cl',
             'contrib/brl/bseg/boxm2/reg/ocl/cl',
             'contrib/brl/bseg/boxm2/vecf/ocl/cl',
             'contrib/brl/bseg/boxm2/volm/cl',
             'contrib/brl/bseg/bstm/ocl/cl']
  cl_dirs = map(lambda x: path_join(env['VIP_VXL_SRC_DIR'], x), cl_dirs)

  cl_dest_dirs = ['boxm2', 'reg', 'vecf', 'volm', 'bstm']
  cl_dest_dirs = map(lambda x: path_join(zipClDir, x), cl_dest_dirs)

  mkpath(zipBinDir)
  mkpath(zipPythonDir)
  mkpath(zipClDir)

  #bin files 
  if not args.skip_bin:
    if rsync:
      pids.append(rsync.sync([path_join(vxlBinDir, '*'+exeExtention)],
                             zipBinDir))
    else:
      files = glob(path_join(vxlBinDir, '*'+exeExtention))
      for file in files:
        copy_file(file, zipBinDir)

  #python libraries
  if rsync:
    pids.append(rsync.sync([path_join(vxlLibDir, '*'+pydExtention)] +
                            map(lambda x: path_join(x, '*'), 
                                pyscript_dirs),
                           zipPythonDir))
  else:
    files = glob(path_join(vxlLibDir, '*'+pydExtention))
    for file in files:
      copy_file(file, zipPythonDir)


    for d in pyscript_dirs:
      copy_tree(d, zipPythonDir)

  #setup python .pth so imports in vxl works without "vxl."
  with open(zipPythonDir+'.pth', 'w') as fid:
    fid.write('vxl')

  #cl files
  if rsync:
    for src, dest in zip(cl_dirs, cl_dest_dirs):
      pids.append(rsync.sync([src+'/'], dest))
  else:
    for src, dest in zip(cl_dirs, cl_dest_dirs):
      copy_tree(src, dest)
    
  files = glob(path_join(env['VIP_VXL_SRC_DIR'], 'contrib', 'brl', 'bbas', 'volm', '*_*.txt'))
  for file in files:
    copy_file(file, zipShareDir)

  #wait for rsyncs to finish
  if rsync:
    for pid in pids:
      pid.wait()

  if windows:
    copy_file(path_join(env['VIP_GLEW_BIN_DIR'], 'glew32.dll'), zipBinDir)
    subprocess.Popen(['7z.exe', 'a', path_join(env['VIP_SRC_DIR'], 'vxl.zip'), 'vxl'], cwd=env['VIP_INSTALL_DIR']).wait();
  else:
    mkpath(zipRoamDir)
    files = glob(path_join(vxlBinDir, '*'+exeExtention))
    roamFile = path_join(zipRoamDir, 'roam')
    for file in files:
      try:
        os.link(roamFile, path_join(zipRoamDir, os.path.basename(file)))
      except OSError:
        pass

if __name__=='__main__':
  main()
