import os
from voxel_globe.tools.subprocessbg import Popen

def zoomify_image(filename, zoomify_dir):
  pid = Popen(['vips', 'dzsave', filename, zoomify_dir, '--layout', 
               'zoomify'])
  pid.wait()

def move_to_sha256(filename):
  from hashlib import sha256
  import voxel_globe.tools.voxel_dir as voxel_dir
  import shutil

  hasher = sha256()
  chunk = 1024*1024*16

  with open(filename, 'rb') as fid:
    data = fid.read(chunk)
    while data:
      hasher.update(data)
      data = fid.read(chunk)
  
  with voxel_dir.image_sha_dir(hasher.hexdigest()) as image_dir:
    try:
      shutil.move(filename, image_dir)
    except:
      pass
    filename = os.path.join(image_dir, os.path.basename(filename))
    return filename
