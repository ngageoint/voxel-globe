import os
from os import environ as env
from glob import glob


from celery.utils.log import get_task_logger
from numpy import sctype2char


from voxel_globe.common_tasks import shared_task, VipTask
from voxel_globe.tools.subprocessbg import Popen

from voxel_globe.ingest.metadata.tasks import Clif as Clif_metadata

logger = get_task_logger(__name__)

CLIF_DATA = Clif_metadata.CLIF_DATA
CLIF_VERSION = Clif_metadata.CLIF_VERSION

class BasePayload(object):
  def __init__(self, task, upload_session_id, ingest_dir):
    from voxel_globe.ingest.models import UploadSession
    self.ingest_dir = ingest_dir
    self.task = task
    self.upload_session = UploadSession.objects.get(id=upload_session_id)

  @classmethod
  def task(cls, fn):
    #fn isn't ACTUALLY used
    def run(self, upload_session_id, ingest_dir):
      obj = cls(self, upload_session_id, ingest_dir)
      return obj.run()
    wrapper1 = shared_task(base=VipTask, bind=True, 
                           name='.'.join((__name__, fn.__name__)))
    wrapper2 = wrapper1(run)
    wrapper2.dbname = cls.dbname
    wrapper2.description = cls.description
    wrapper2.payload_ingest=True
    return wrapper2

  def zoomify_add_image(self, filename, width, height, bands, pixel_format):
    from hashlib import sha256
    import urllib

    import voxel_globe.meta.models

    hasher = sha256()
    chunk = 1024*1024*16

    with open(filename, 'rb') as fid:
      data = fid.read(chunk)
      while data:
        hasher.update(data)
        data = fid.read(chunk)
    zoomify_name = os.path.join(os.path.split(filename)[0], hasher.hexdigest()+'_zoomify')
    #zoomify_name = os.path.splitext(filename)[0] + '_zoomify'
    pid = Popen(['vips', 'dzsave', filename, zoomify_name, '--layout', 
                 'zoomify'])
    pid.wait()

    #convert the slashes to URL slashes 
    relative_file_path = urllib.pathname2url(os.path.relpath(filename, 
        env['VIP_IMAGE_SERVER_ROOT']))
    basename = os.path.split(filename)[-1]
    relative_zoom_path = urllib.pathname2url(os.path.relpath(zoomify_name, 
        env['VIP_IMAGE_SERVER_ROOT']))

    img = voxel_globe.meta.models.Image(
          name="%s Upload %s (%s) Frame %s" % (self.meta_name,
                                               self.upload_session.name, 
                                               self.upload_session.id, 
                                               basename), 
          imageWidth=width, imageHeight=height, 
          numberColorBands=bands, pixelFormat=pixel_format, fileFormat='zoom', 
          imageUrl='%s://%s:%s/%s/%s/' % (env['VIP_IMAGE_SERVER_PROTOCOL'], 
                                         env['VIP_IMAGE_SERVER_HOST'], 
                                         env['VIP_IMAGE_SERVER_PORT'], 
                                         env['VIP_IMAGE_SERVER_URL_PATH'], 
                                         relative_zoom_path),
          originalImageUrl='%s://%s:%s/%s/%s' % (
              env['VIP_IMAGE_SERVER_PROTOCOL'], 
              env['VIP_IMAGE_SERVER_HOST'], 
              env['VIP_IMAGE_SERVER_PORT'], 
              env['VIP_IMAGE_SERVER_URL_PATH'], 
              relative_file_path),
          service_id=self.task.request.id,
          original_filename=basename)
    img.save()
     
    self.image_collection.images.add(img)


  def create_image_collection(self):
    import voxel_globe.meta.models as models

    self.image_collection = models.ImageCollection(
        name="%s %s:" % (self.upload_session.name, self.meta_name,),
        service_id = self.task.request.id)
    self.image_collection.save()


class ImageSequence(BasePayload):
  dbname = 'images'
  description = 'Image Sequence'
  meta_name = description

  def run(self):
    from vsi.io.image import imread

    import voxel_globe.meta.models as models

    self.create_image_collection()

    filenames = glob(os.path.join(self.ingest_dir, '*'))
    filenames.sort()

    image_index=0

    for index,filename in enumerate(filenames):
      img = imread(filename)
      if img is None: #If not an image
        continue      #NEXT!

      image_index += 1

      self.task.update_state(state='PROCESSING',
          meta={'stage':'File %s (%d of %d)' % (filename, index, 
                                                len(filenames))})

      pixel_format = sctype2char(img.dtype())

      self.zoomify_add_image(filename, img.shape()[1], img.shape()[0], 
                             img.bands(), pixel_format)

    return self.image_collection.id


class Clif(BasePayload):
  dbname = 'clif'
  description = 'Columbus Large Image Format'
  meta_name = 'CLIF'

  def run(self):
    import numpy as np
    import PIL.Image

    from vsi.iglob import glob

    import voxel_globe.meta.models

    pixel_format = CLIF_DATA[CLIF_VERSION]['pixel_format']
    width = CLIF_DATA[CLIF_VERSION]['width']
    height = CLIF_DATA[CLIF_VERSION]['height']
    bands = CLIF_DATA[CLIF_VERSION]['bands']
    
    files = glob(os.path.join(self.ingest_dir, '*'+os.extsep+'raw'), False)
    files.sort()

    self.create_image_collection()

    for index, filename in enumerate(files):
      self.task.update_state(state='PROCESSING', 
          meta={'stage':'File %s (%d of %d)' % (filename, index+1, 
                                                len(files))})
      logger.debug('Processing %s (%d of %d)', filename, index+1, len(files))

      basename = os.path.basename(filename)
      img_filename = os.extsep.join([os.path.splitext(filename)[0], 'png'])

      with open(filename, 'rb') as fid:
        data = fid.read()
      img = np.fromstring(data, 
          dtype=CLIF_DATA[CLIF_VERSION]['dtype']).reshape(width, height).T
      img2 = PIL.Image.fromarray(img)
      img2.save(img_filename)

      self.zoomify_add_image(img_filename, width, height, bands, pixel_format)

    return self.image_collection.id


@ImageSequence.task
def images():
  pass

@Clif.task
def clif():
  pass
