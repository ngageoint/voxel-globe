import os

def split_clif(filename):
  ''' Return dir, camera_id, image_number, extention'''
  dirname = os.path.dirname(filename)
  filename = os.path.basename(filename)
  (filename, extention) = os.path.splitext(filename)
  (camera_id, image_number) = filename.split('-')
  return (dirname, camera_id, image_number, extention)