import os


from celery.utils.log import get_task_logger


from voxel_globe.common_tasks import shared_task, VipTask
from .tools import match_images, load_voxel_globe_metadata, create_scene


logger = get_task_logger(__name__)

@shared_task(base=VipTask, bind=True)
def krt(self, image_collection_id, upload_session_id, image_dir):
  from glob import glob


  from vsi.io.krt import Krt

  from voxel_globe.ingest.models import UploadSession
  from voxel_globe.meta.models import ImageCollection
  from voxel_globe.tools.camera import save_krt


  upload_session = UploadSession.objects.get(id=upload_session_id)

  json_config = load_voxel_globe_metadata(image_dir)

  try:
    origin_xyz = (json_config['origin']['longitude'], 
              json_config['origin']['latitude'], 
              json_config['origin']['altitude'])
  except (TypeError, KeyError):
    origin_xyz = (0,0,0)

  try:
    srid = json_config['origin']['srid']
  except (TypeError, KeyError):
    srid = 4326

  try:
    bbox_min = (json_config['bbox']['east'], 
                json_config['bbox']['south'], 
                json_config['bbox']['bottom'])
  except (TypeError, KeyError):
    bbox_min = [0,0,0]

  try:
    bbox_max = (json_config['bbox']['west'], 
                json_config['bbox']['north'], 
                json_config['bbox']['top'])
  except (TypeError, KeyError):
    bbox_max = [0,0,0]

  try:
    gsd = json_config['gsd']
  except (TypeError, KeyError):
    gsd = 1


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

  image_collection = ImageCollection.objects.get(id=image_collection_id)

  matches = match_images(image_collection.images.all(), krts.keys(), 
                         json_config)

  for match in matches:
    krt_1 = krts[match]
    logger.debug('%s matched to %s', match, matches[match].original_filename)
    save_krt(self.request.id, matches[match], krt_1.k, krt_1.r, krt_1.t, 
             origin_xyz)

  scene = create_scene(self.request.id, 
      'Image Sequence Origin %s' % upload_session.name, 
      'SRID=%d;POINT(%0.18f %0.18f %0.18f)' % \
      (srid, origin_xyz[0], origin_xyz[1], origin_xyz[2]),
      bbox_min_point='POINT(%0.18f %0.18f %0.18f)' % bbox_min,
      bbox_max_point='POINT(%0.18f %0.18f %0.18f)' % bbox_max,
      default_voxel_size_point='POINT(%0.18f %0.18f %0.18f)' % \
                               (gsd,gsd,gsd))

  image_collection.scene = scene
  image_collection.save()


krt.MAX_SIZE = 1024 #Max size a krt can be. This helps prevent uselessly trying
#to parse the payload data, etc...
krt.dbname = 'krt'
krt.description = 'VXL KRT perspective cameras'
krt.metadata_ingest=True
