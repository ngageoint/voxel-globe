import os


from celery.utils.log import get_task_logger


from voxel_globe.common_tasks import shared_task, VipTask
from .tools import match_images, load_voxel_globe_metadata, create_scene


logger = get_task_logger(__name__)

### These need to be CLASSES actually, and call common parts via methods! :(

class BaseMetadata(object):
  def __init__(self):
    pass
  
  # @classmethod
  # def decorate_hmm(cls):
  #   def wrapper(fn):
  #     fn.dbname = cls.dbname
  #     print '1'
  #     return fn
  #   return wrapper

  @classmethod
  def task(cls, fn):
    def wrapper(self):
      return fn()
    wrapper1 = shared_task(base=VipTask, bind=True)
    wrapper2 = wrapper1(fn)
    wrapper2.dbname = cls.dbname
    return wrapper2

  def parse_json(self, gsd=1, srid=4326, etc=0):
    pass

class Krt(BaseMetadata):
  dbname = 'krt'
  description = 'VXL KRT perspective cameras'
  
  def __init__(self):
    pass

  def run(self, task, image_collection_id, upload_session_id, image_dir):
    pass

#This WORKS I believe
#This pattern isn't vulnerable to the class method tasks caveats, and since
#This is in a module, it would have been ugly and a pain
@Krt.task
def test_krt(self):
  print 'woot'
  print test_krt.dbname
  return True


@shared_task(base=VipTask, bind=True)
def krt(self, image_collection_id, upload_session_id, image_dir):
  from glob import glob


  from vsi.io.krt import Krt

  from voxel_globe.ingest.models import UploadSession
  from voxel_globe.meta.models import ImageCollection
  from voxel_globe.tools.camera import save_krt


  self.update_state(state='Processing', meta={'stage':'metadata'})

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


@shared_task(base=VipTask, bind=True)
def arducopter(self, image_collection_id, upload_session_id, image_dir):
  import numpy as np


  from vsi.iglob import glob
  from vsi.io.krt import Krt

  from voxel_globe.ingest.models import UploadSession
  from voxel_globe.meta.models import ImageCollection
  from voxel_globe.tools.camera import save_krt

  from .tools import load_arducopter_metadata


  self.update_state(state='Processing', meta={'stage':'metadata'})

  upload_session = UploadSession.objects.get(id=upload_session_id)

  image_collection = ImageCollection.objects.get(id=image_collection_id)

  metadata_filename = glob(os.path.join(image_dir, 
                           '*_adj_tagged_images.txt'), False)

  if not len(metadata_filename) == 1:
    logger.error('Only one metadata file should have been found, '
                 'found %d instead', len(metadata_filename))

  metadata_filename = metadata_filename[0]

  date = time_of_day = '' 
  try:
    (date, time_of_day) = os.path.split(metadata_filename)[1].split(' ')
    time_of_day = time_of_day.split('_', 1)[0]
  except:
    time_of_day = ''

  image_collection.name="Arducopter Upload %s %s %s (%s)" \
      % (upload_session.name, date, time_of_day, upload_session_id)


  json_config = load_voxel_globe_metadata(image_dir)


  try:
    srid = json_config['origin']['srid']
  except (TypeError, KeyError):
    srid = 7428

  metadata = load_arducopter_metadata(metadata_filename)

  #Do not worry about height or GSD, these will be filled in via sfm
  #just get the bbox in so that the viewer knows the fov. So calculate via 
  #metadata values
  try:
    origin_xyz = (json_config['origin']['longitude'], 
              json_config['origin']['latitude'], 
              json_config['origin']['altitude'])
  except (TypeError, KeyError):
    origin_xyz = (0,0,0)

  try:
    bbox_min = (json_config['bbox']['east'], 
                json_config['bbox']['south'], 
                json_config['bbox']['bottom'])
  except (TypeError, KeyError):
    bbox_min = (0,0,0)

  try:
    bbox_max = (json_config['bbox']['west'], 
                json_config['bbox']['north'], 
                json_config['bbox']['top'])
  except (TypeError, KeyError):
    bbox_max = (0,0,0)

  try:
    gsd = json_config['gsd']
  except (TypeError, KeyError):
    gsd = 1


  for meta in metadata:
    try:
      img = image_collection.images.get(
          name__icontains='Frame %s' % meta.filename)
      k = np.eye(3);
      k[0,2] = img.imageWidth/2;
      k[1,2] = img.imageHeight/2;      
      r = np.eye(3);
      t = [0, 0, 0];
      origin = meta.llh_xyz;
      save_krt(self.request.id, img, k, r, t, origin, srid=7428);
    except Exception as e:
      logger.warning('%s', e)
      logger.error('Could not match metadata entry for %s' % meta.filename)

  #TODO replace this above in json config section. Who cares if I look through
  #meta multiple times
  origin_xyz = np.mean(np.array(map(lambda x:x.llh_xyz, metadata)), 0)

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

arducopter.dbname = 'arducopter'
arducopter.description = 'Arducopter GPS metadata'
arducopter.metadata_ingest=True
