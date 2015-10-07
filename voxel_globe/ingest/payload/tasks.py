import os
from os import environ as env
from glob import glob
import urllib


from celery.utils.log import get_task_logger
from numpy import sctype2char


from voxel_globe.common_tasks import shared_task, VipTask
from voxel_globe.tools.subprocessbg import Popen


logger = get_task_logger(__name__)


@shared_task(base=VipTask, bind=True)
def images(self, upload_session_id, image_dir):
  from vsi.io.image import imread


  from voxel_globe.ingest.models import UploadSession
  import voxel_globe.meta.models as models

  from voxel_globe.ingest.metadata.tools import load_voxel_globe_metadata

  upload_session = UploadSession.objects.get(id=upload_session_id)

  config = load_voxel_globe_metadata(image_dir)

  try:
    date = config['date']
  except (TypeError, KeyError):
    date = ''

  try:
    time_of_day = config['time']
  except (TypeError, KeyError):
    time_of_day = ''

  image_collection = models.ImageCollection.create(
      name="Image Sequence Upload %s %s %s (%s)" % (upload_session.name, date, 
                                                    time_of_day, 
                                                    upload_session_id), 
      service_id = self.request.id)
  image_collection.save()

  filenames = glob(os.path.join(image_dir, '*'))
  filenames.sort()

  image_index=0

  for index,filename in enumerate(filenames):
    img = imread(filename)
    if img is None: #If not an image
      continue      #NEXT!

    image_index += 1

    self.update_state(state='PROCESSING',
                      meta={'stage':'File %s (%d of %d)' % (filename, index, 
                                                            len(filenames))})

    zoomify_name = os.path.splitext(filename)[0] + '_zoomify'

    pid = Popen(['vips', 'dzsave', filename, zoomify_name, '--layout', 'zoomify'])
    pid.wait();

    relative_file_path = urllib.pathname2url(os.path.relpath(filename, 
        env['VIP_IMAGE_SERVER_ROOT']))
    basename = os.path.split(filename)[-1]
    relative_zoom_path = urllib.pathname2url(os.path.relpath(zoomify_name, 
        env['VIP_IMAGE_SERVER_ROOT']))

    pixel_format = sctype2char(img.dtype())

    image = models.Image.create(
        name="Image Sequence Upload %s (%s) Frame %s (%d)" % (
            upload_session.name, upload_session_id, basename, image_index), 
        imageWidth=img.shape()[1], imageHeight=img.shape()[0], 
        numberColorBands=img.bands(), pixelFormat=pixel_format, 
        fileFormat='zoom', 
        imageUrl='%s://%s:%s/%s/%s/' % (env['VIP_IMAGE_SERVER_PROTOCOL'], 
                                        env['VIP_IMAGE_SERVER_HOST'], 
                                        env['VIP_IMAGE_SERVER_PORT'], 
                                        env['VIP_IMAGE_SERVER_URL_PATH'], 
                                        relative_zoom_path),
        originalImageUrl='%s://%s:%s/%s/%s' %(env['VIP_IMAGE_SERVER_PROTOCOL'], 
                                              env['VIP_IMAGE_SERVER_HOST'], 
                                              env['VIP_IMAGE_SERVER_PORT'], 
                                              env['VIP_IMAGE_SERVER_URL_PATH'], 
                                              relative_file_path),
        original_filename=basename,
        service_id=self.request.id)
    image.save()

    image_collection.images.add(image)

  return image_collection.id

images.dbname = 'images'
images.description = 'Image Sequence'
images.payload_ingest=True
