#!/usr/bin/env bash

_=''''
exec $(dirname $0)/../../wrap python $0 "${@}"
' '''
#!/usr/bin/env python

import zipfile
import os
from distutils.dir_util import remove_tree
from glob import glob

import argparse

lib_infos = (('Cesium-1.23.zip', None, 'cesium'), #https://cesiumjs.org/downloads.html
             ('jQuery-File-Upload-9.12.5.zip',
              'jQuery-File-Upload-9.12.5', 'fileUpload'), #https://github.com/blueimp/jQuery-File-Upload/releases
             ('jquery-ui-1.11.4.zip', 'jquery-ui-1.11.4', 'jquery-ui'), #https://jqueryui.com/download/all/
             ('jquery-ui-themes-1.11.4.zip', 'jquery-ui-themes-1.11.4', 'jquery-ui-themes'), #https://jqueryui.com/download/all/
             ('potree-1.3-patch1.zip', 'potree', 'potree'), #./just build_potree
             ('v3.17.1-dist.zip', 'v3.17.1-dist', 'OpenLayers3')) #http://openlayers.org/download/

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
