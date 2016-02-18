import os
from voxel_globe.tools.subprocessbg import Popen

def zoomify_image(filename, zoomify_dir):
  pid = Popen(['vips', 'dzsave', filename, zoomify_dir, '--layout', 
               'zoomify'])
  pid.wait()
