import os

from voxel_globe.common_tasks import shared_task, VipTask
from .tools import match_images, load_voxel_globe_metadata

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__);

@shared_task(base=VipTask, bind=True)
def krt(self, image_collection_id, upload_session_id, image_dir):
  from glob import glob

  from vsi.io.krt import Krt

  from voxel_globe.ingest.models import UploadSession
  from voxel_globe.meta.models import ImageCollection
  from voxel_globe.tools.camera import save_krt
  upload_session = UploadSession.objects.get(id=upload_session_id)

  json_config = load_voxel_globe_metadata(image_dir)
  origin = [0,0,0]
  try:
    origin = [json_config['origin']['longitude'], 
              json_config['origin']['latitude'], 
              json_config['origin']['altitude']]
  except (TypeError, KeyError):
    pass

  
  metadata_filenames = glob(os.path.join(image_dir, '*'))

  krts={}

  for metadata_filename in metadata_filenames:
    if os.stat(metadata_filename).st_size <= krt.MAX_SIZE:
      try:
        krt_1 = Krt.load(metadata_filename)
        krts[os.path.basename(metadata_filename)] = krt_1
      except: #Hopefully non-krts throw an exception when loading
        import traceback as tb
        logger.debug('Non-KRT parsed: %s', tb.format_exc())

  matches = match_images(
      ImageCollection.objects.get(id=image_collection_id).images.all(), 
      krts.keys(), json_config)

  for match in matches:
    krt_1 = krts[match]
    logger.info('k: %s r: %s t: %s', krt_1.k, krt_1.r, krt_1.t)
    save_krt(self.request.id, matches[match], krt_1.k, krt_1.r, krt_1.t, origin)


krt.MAX_SIZE = 1024 #Max size a krt can be. This helps prevent uselessly trying
#to parse the payload data, etc...
krt.dbname = 'krt'
krt.description = 'VXL KRT perspective cameras'
krt.metadata_ingest=True
