from celery.utils.log import get_task_logger
logger = get_task_logger(__name__);

def convert_image(filename, output_filename, image_type, options=None):
  '''Convert image to another type 

     Arguments
     filename - input filename
     output_filename - output filename
     image_type - GDAL File format'''
  from osgeo import gdal

  source_file = gdal.Open(filename)
  driver = gdal.GetDriverByName(image_type)
  destination = driver.CreateCopy(output_filename, source_file, 
                                  options=options)
