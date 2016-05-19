#!/usr/bin/env python 

import os
from os import environ as env
from os.path import join as path_join
from distutils.dir_util import mkpath
import subprocess

try:
  from shlex import quote
except:
  from pipes import quote

if os.name=='nt':
  import ntpath

from ast import literal_eval

import argparse

def get_parser():
  parser = argparse.ArgumentParser(
    description="Builds vxl")

  parser.add_argument('--rebuild', '-r', default=False, action='store_true',
    help='Rebuild vxl, don\'t directly rerun cmake')
  parser.add_argument('--cmake', '-c', default=False, action='store_true',
    help='Run cmake only')
  parser.add_argument('--verbose', '-v', default=False, action='store_true',
    help='Run make program with verbose on')
  return parser

def main():
  parser = get_parser()
  args = parser.parse_args()

  vxlDir = path_join(env['VIP_VXL_BUILD_DIR'], env['VIP_VXL_BUILD_TYPE'])
  mkpath(vxlDir)
  os.chdir(vxlDir)


  if os.name == 'nt':
    if not os.path.exists(env['VIP_GLEW_INCLUDE_DIR']):
      print "You are missing Glew"
      from voxel_globe.tools.wget import download
      print "Downloading..."
      zipFile = os.path.join(env['VIP_GLEW_INCLUDE_DIR'], '../../glew.zip')
      dater = download('http://downloads.sourceforge.net/project/glew/glew/' 
                       '1.12.0/glew-1.12.0-win32.zip', 
                       zipFile)
      print "Unpacking..."
      subprocess.Popen(['7z.exe', 'x', zipFile], 
          cwd=os.path.join(env['VIP_GLEW_INCLUDE_DIR'], '../..')).wait()
    from distutils.msvc9compiler import find_vcvarsall
    platform = env.get('VIP_CMAKE_PLATFORM', None)
    if 'VCVARSALL' not in env:
      if platform and platform.lower().startswith('visual'):
        msvcVersion = int(platform.split(' ')[2])
        vcvarall = find_vcvarsall(msvcVersion)
      else:
        for v in range(14, 8, -1): 
        #Start with version 2015(14), and got back to (8),
        #before that its 32 bit only, and we don't care about that
          vcvarall = find_vcvarsall(v)
          if not vcvarall is None:
            if platform.lower() != 'ninja':
              platform = 'Visual Studio %d Win64' % v
            break
      env['VCVARSALL'] = vcvarall
  else:
    platform = env['VIP_CMAKE_PLATFORM']

  if not args.rebuild:
    cmake_options = []
    
    cmake_options += ['-G', platform]

    #HIGHLY recommended for ninja
    if 'VIP_CMAKE_MAKE_PROGRAM' in env:
      cmake_options += ['-D', 'CMAKE_MAKE_PROGRAM='+\
                              env['VIP_CMAKE_MAKE_PROGRAM']]
    #More or less required for ninja in windows
    if 'VIP_CMAKE_COMPILER' in env:
      cmake_options += ['-D', 'CMAKE_C_COMPILER='+env['VIP_CMAKE_COMPILER']]
      cmake_options += ['-D', 'CMAKE_CXX_COMPILER='+ env['VIP_CMAKE_COMPILER']]


    cmake_options += ['-D', 'CMAKE_BUILD_TYPE='+env['VIP_VXL_BUILD_TYPE']]
    
    if 'VIP_OPENCL_INCLUDE_PATH' in env:
      cmake_options += ['-D', 'OPENCL_INCLUDE_PATH='+
                        env['VIP_OPENCL_INCLUDE_PATH']]
    if 'VIP_OPENCL_LIBRARY_PATH' in env:
      cmake_options += ['-D', 'OPENCL_LIBRARY_PATH='+
                        env['VIP_OPENCL_LIBRARY_PATH']]
    if 'VIP_OPENCL_NVIDIA_LIBRARY_PATH' in env:
      cmake_options += ['-D', 'OPENCL_NVIDIA_LIBRARY_PATH='+
                        env['VIP_OPENCL_NVIDIA_LIBRARY_PATH']]
    if 'VIP_GLEW_INCLUDE_DIR' in env:
      cmake_options += ['-D', 'GLEW_INCLUDE_DIR='+env['VIP_GLEW_INCLUDE_DIR']]
    if 'VIP_GLEW_LIBRARY' in env:
      cmake_options += ['-D', 'GLEW_LIBRARY='+env['VIP_GLEW_LIBRARY']]

    if platform=="Eclipse CDT4 - Unix Makefiles":
      cmake_options += ['-D', 'CMAKE_ECLIPSE_GENERATE_SOURCE_PROJECT=True']

    cmake_options += ['-D', 'CMAKE_INSTALL_PREFIX='+
                   path_join(vxlDir, 'install')]

    cmake_options += ['-D', 'EXECUTABLE_OUTPUT_PATH='+
                   path_join(vxlDir, 'bin')]

    cmake_options += ['-D', 'PYTHON_INCLUDE_DIR='+
                      env['VIP_PYTHON_INCLUDE_DIR'],
                      '-D', 'PYTHON_LIBRARY='+
                      env['VIP_PYTHON_LIBRARY'],
                      '-D', 'PYTHON_INCLUDE_DIR2='+
                      env['VIP_PYTHON_INCLUDE_DIR'],
                      '-D', 'PYTHON_EXECUTABLE='+
                      env['VIP_PYTHON_EXECUTABLE']]
                      
    tmp = env.pop('VIP_CMAKE_ECLIPSE', None)
    if tmp:
      cmake_options += ['-D', 'CMAKE_ECLIPSE_EXECUTABLE='+tmp]

    # Pretty open options section. User can in theory, override anything here  

    tmp = env.pop('VIP_VXL_CMAKE_OPTIONS', None)
    if tmp:
      cmake_options += literal_eval('[' + tmp + ']')
      #Sure, this may be generally unsafe, but only the user administrating the 
      #computer should be able to set and run this, so I choose to trust them
      #Update. literal_eval should be "safe"...er

    tmp = env.pop('VIP_VXL_CMAKE_ENTRIES', None)
    if tmp:
      tmp = literal_eval('[' + tmp + ']')
      for entry in tmp:
        cmake_options += ['-D', entry]

    #Run CMake
    if os.name=='nt':
      if platform.lower()=='ninja':
        args = [ntpath.normpath(os.path.join(env['VIP_INSTALL_DIR'], 
                                             'run_vcvarsall.bat'))]
        cmd = args + [env['VIP_CMAKE']] + cmake_options \
            + [env['VIP_VXL_SRC_DIR']]
      else:
        cmd = [env['VIP_CMAKE']] + cmake_options + [env['VIP_VXL_SRC_DIR']]
    else:
      cmd = [env['VIP_CMAKE']] + cmake_options + [env['VIP_VXL_SRC_DIR']]
    print ' '.join([quote(x) for x in cmd])
    pid = subprocess.Popen(cmd)
    pid.wait()

  if args.cmake:
    return

  #Make it
  if os.name=='nt':
    if platform.lower()=='ninja':
      cmd = [ntpath.normpath(os.path.join(env['VIP_INSTALL_DIR'], 
                                           'run_vcvarsall.bat')), 
              env['VIP_CMAKE_NINJA']]
    else:
      cmd = [ntpath.normpath(os.path.join(env['VIP_INSTALL_DIR'], 
                                           'run_vcvarsall.bat')), 
              'devenv', 'vxl.sln', '/Build', 
              env['VIP_VXL_BUILD_TYPE']+'^^^|x64']
      #The ^^^ is for Stupid batch escape limitation with | Thank you windows! :(
    
    if platform.lower() != 'ninja':
      if args.verbose:
        pass #No idea right now
      print "Loading vxl solution... This may take a few minutes."
  else:
    cmd = [env['VIP_CMAKE_MAKE_PROGRAM'], '-j', '10']
    if args.verbose:
      if platform.lower() != 'ninja':
        cmd += ['VERBOSE=1']

  if args.verbose:
    if platform.lower() == 'ninja':
      cmd += ['-v']

  pid = subprocess.Popen(cmd, cwd=vxlDir)
  pid.wait()

if __name__=='__main__':
  main()