:; $(dirname $0)/../../_wrap.bsh python -x $0 "${@}"; exit $? ; ^
'''
@echo off
%~dp0../../wrap.bat python -x %~dp0%~nx0 %*
goto :eof
'''

import zipfile
import os
from distutils.dir_util import remove_tree
from glob import glob

import sys
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
  #Add a compatibility dir for python versions younger than 2.7
  sys.path.append(os.path.join(os.env['VIP_INSTALL_DIR'], 'compat'))
import argparse

lib_infos = (('Cesium-1.13.zip', None, 'cesium'),
             ('jQuery-File-Upload-9.11.2.zip', 
              'jQuery-File-Upload-9.11.2', 'fileUpload'),
             ('jquery-ui-1.11.4.zip', 'jquery-ui-1.11.4', 'jquery-ui'),
             ('jquery-ui-themes-1.11.4.zip', 'jquery-ui-themes-1.11.4', 'jquery-ui-themes'),
             ('potree-1.3.zip', 'potree-1.3', 'potree'),
             ('v3.9.0-dist.zip', 'v3.9.0-dist', 'OpenLayers3'))

def unzip(filename, base_dir):
  print 'Unzipping', filename, base_dir
  with zipfile.ZipFile(filename, 'r') as z:
    z.extractall(base_dir)

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--remove', default=False, action='store_true',
     help='Remove deployed library directories rather than unzip them')
  return parser.parse_args()

def main(base_dir):
  opts = parse_args()

  #for old_dir in glob(os.path.join(base_dir, '*/')):
  #  if os.path.exists(old_dir):
  #    remove_tree(old_dir)
  #   print "Removing", old_dir

  for (zip_filename, unzip_dir, dest_dir) in lib_infos:
    zip_filename = os.path.join(base_dir, zip_filename)
    assert(dest_dir.strip(' /\\.') != '')
    dest_dir = os.path.join(base_dir, dest_dir)

    #Remove the old
    if os.path.exists(dest_dir):
      print "Removing", dest_dir
      remove_tree(dest_dir)
    
    if not opts.remove:
      if unzip_dir is not None:
        unzip(zip_filename, base_dir)

        unzip_dir = os.path.join(base_dir, unzip_dir)
        print "Moving %s to %s" % (unzip_dir, dest_dir)
        os.rename(unzip_dir, dest_dir)
      else:
        os.makedirs(dest_dir)
        unzip(zip_filename, dest_dir)

if __name__=='__main__':
  main(os.environ['VIP_DJANGO_STATIC_COMMON'])
