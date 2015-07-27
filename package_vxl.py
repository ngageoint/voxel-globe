#!/usr/bin/env python

import os
from os import environ as env
from os.path import join as path_join
from distutils.dir_util import mkpath, copy_tree
from distutils.file_util import copy_file
import subprocess
from glob import glob

if __name__=='__main__':
  if os.name == 'nt':
    exeExtention = '.exe'
    pydExtention = '.pyd'
  else:
    exeExtention = ''
    pydExtention = '.so'
  
  zipDir = env['VIP_INSTALL_DIR']
  if os.name == 'nt':
    zipDir = path_join(zipDir, 'vxl')
    #Cause that's how its done in windows... :(

  vxlBinDir = env['VIP_VXL_BUILD_BIN_DIR']
  vxlLibDir = env['VIP_VXL_BUILD_LIB_DIR']
  
  zipBinDir = path_join(zipDir, 'bin')
  zipRoamDir = path_join(zipDir, 'roam')
  zipPythonDir = path_join(zipDir, 'lib', 'python2.7', 'site-packages', 'vxl')
  zipShareDir = path_join(zipDir, 'share', 'vxl')
  zipClDir = path_join(zipShareDir, 'cl')

  mkpath(zipBinDir)
  mkpath(zipPythonDir)
  mkpath(zipClDir)
  
  files = glob(path_join(vxlBinDir, '*'+exeExtention))
  for file in files:
    copy_file(file, zipBinDir)
  
  files = glob(path_join(vxlLibDir, '*'+pydExtention))
  for file in files:
    copy_file(file, zipPythonDir)
  for d in ['contrib/brl/bseg/boxm2/pyscripts',
            'contrib/brl/bseg/boxm2_multi/pyscripts',
            'contrib/brl/bseg/bstm/pyscripts',
            'contrib/brl/bseg/bvxm/pyscripts']:
    copy_tree(path_join(env['VIP_VXL_SRC_DIR'], d), zipPythonDir)

  with open(zipPythonDir+'.pth', 'w') as fid:
    fid.write('vxl')

  for d,n in zip(['contrib/brl/bseg/boxm2/ocl/cl',
                  'contrib/brl/bseg/boxm2/reg/ocl/cl',
                  'contrib/brl/bseg/boxm2/vecf/ocl/cl',
                  'contrib/brl/bseg/boxm2/volm/cl',
                  'contrib/brl/bseg/bstm/ocl/cl'], 
                 ['boxm2', 'reg', 'vecf', 'volm', 'bstm']):
    copy_tree(path_join(env['VIP_VXL_SRC_DIR'], d), path_join(zipClDir, n))
    
  files = glob(path_join(env['VIP_VXL_SRC_DIR'], 'contrib', 'brl', 'bbas', 'volm', '*_*.txt'))
  for file in files:
    copy_file(file, zipShareDir)

  if os.name == 'nt':
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
