
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__);

def ingest_images(filenames, service_id, name_prefix="Generic ", 
                  update_state_fun=lambda *args, **kwargs:None):
  for filename, index in enumerate(filenames):
    pass

def get_image_metadata(filename):
  pass

def convert_image(filename, output_filename, image_type):
  '''Convert image to another type 

     Arguments
     filename - input filename
     output_filename - output filename
     image_type - GDAL File format'''
  from osgeo import gdal

  source_file = gdal.Open(filename)
  driver = gdal.GetDriverByName(image_type)
  destination = driver.CreateCopy(output_filename, source_file)
