import os


from celery.utils.log import get_task_logger
import numpy as np


from voxel_globe.common_tasks import shared_task, VipTask
from voxel_globe.tools.camera import save_krt
from .tools import match_images, match_attributes, load_voxel_globe_metadata, create_scene

logger = get_task_logger(__name__)

### These need to be CLASSES actually, and call common parts via methods! :(

#New idea, add "get_focal_length(filename)" to BaseMetadata. It will use the json_config
#to either look for a fixed focal length, or a per image filename  focal length
#from the json config file, just like how matching works. 
#Then add "get_focal_length(filename)" it to a specific metadata parser, this do it's best
#and then call super... Remember, the json_config should always overwrite EVERYTHING else
#do same for date, time_of_day, etc... 

class BaseMetadata(object):
  def __init__(self, task, image_collection_id, upload_session_id, ingest_dir):
    from voxel_globe.ingest.models import UploadSession
    from voxel_globe.meta.models import ImageCollection

    self.task = task
    self.image_collection = ImageCollection.objects.get(id=image_collection_id)
    self.upload_session = UploadSession.objects.get(id=upload_session_id)
    self.ingest_dir = ingest_dir
  
  @classmethod
  def task(cls, fn):
    #fn isn't ACTUALLY used
    def run(self, image_collection_id, upload_session_id, ingest_dir):
      obj = cls(self, image_collection_id, upload_session_id, ingest_dir)
      return obj.run()
    wrapper1 = shared_task(base=VipTask, bind=True, 
                           name='.'.join((__name__, fn.__name__)))
    wrapper2 = wrapper1(run)
    wrapper2.dbname = cls.dbname
    wrapper2.description = cls.description
    wrapper2.metadata_ingest=True
    return wrapper2

  def parse_json(self, origin_xyz=(0,0,0), gsd=1, srid=4326,
                 bbox_min=(0,0,0), bbox_max=(0,0,0),
                 date='', time_of_day=''):
    self.json_config = load_voxel_globe_metadata(self.ingest_dir)

    try:
      self.origin_xyz = (self.json_config['origin']['longitude'], 
                         self.json_config['origin']['latitude'], 
                         self.json_config['origin']['altitude'])
    except (TypeError, KeyError):
      self.origin_xyz = origin_xyz

    try:
      self.srid = self.json_config['origin']['srid']
    except (TypeError, KeyError):
      self.srid = srid

    try:
      self.bbox_min = (self.json_config['bbox']['east'], 
                       self.json_config['bbox']['south'], 
                       self.json_config['bbox']['bottom'])
    except (TypeError, KeyError):
      self.bbox_min = bbox_min

    try:
      self.bbox_max = (self.json_config['bbox']['west'], 
                       self.json_config['bbox']['north'], 
                       self.json_config['bbox']['top'])
    except (TypeError, KeyError):
      self.bbox_max = bbox_min

    try:
      self.gsd = self.json_config['gsd']
    except (TypeError, KeyError):
      self.gsd = gsd

    try:
      self.date = self.json_config['date']
    except (TypeError, KeyError):
      self.date = date

    try:
      self.time_of_day = self.json_config['time_of_day']
    except (TypeError, KeyError):
      self.time_of_day = time_of_day

  def save_scene(self):
    self.image_collection.name += '%s %s %s' % (self.meta_name, self.date, 
                                                self.time_of_day)

    self.image_collection.scene = create_scene(self.task.request.id, 
        '%s Origin %s' % (self.meta_name, self.upload_session.name), 
        'SRID=%d;POINT(%0.18f %0.18f %0.18f)' % \
        (self.srid, self.origin_xyz[0], self.origin_xyz[1], 
         self.origin_xyz[2]),
        bbox_min_point='POINT(%0.18f %0.18f %0.18f)' % self.bbox_min,
        bbox_max_point='POINT(%0.18f %0.18f %0.18f)' % self.bbox_max,
        default_voxel_size_point='POINT(%0.18f %0.18f %0.18f)' % \
                                 (self.gsd,self.gsd,self.gsd))
    self.image_collection.save()

class Krt(BaseMetadata):
  dbname = 'krt'
  description = 'VXL KRT perspective cameras'
  meta_name='KRT'
  MAX_SIZE = 1024

  def run(self):
    from glob import glob

    from vsi.io.krt import Krt as KrtCamera

    self.task.update_state(state='Processing', meta={'stage':'metadata'})

    self.parse_json()

    metadata_filenames = glob(os.path.join(self.ingest_dir, '*'))

    krts={}

    for metadata_filename in metadata_filenames:
      if os.stat(metadata_filename).st_size <= Krt.MAX_SIZE:
        try:
          krt_1 = KrtCamera.load(metadata_filename)
          krts[os.path.basename(metadata_filename)] = krt_1
        except: #Hopefully non-krts throw an exception when loading
          import traceback as tb
          logger.debug('Non-KRT parsed: %s', tb.format_exc())

    matches = match_images(self.image_collection.images.all(), krts.keys(), 
                           self.json_config)

    matching_attributes = match_attributes(self.image_collection.images.all(), 
                                           self.json_config)

    for match in matches:
      krt_1 = krts[match]
      attributes = ''
      logger.debug('%s matched to %s', match, matches[match].original_filename)
      save_krt(self.task.request.id, matches[match], krt_1.k, krt_1.r, krt_1.t, 
              self.origin_xyz, srid=self.srid,
              attributes=matching_attributes.get(matches[match].original_filename, 
                                                 {}))

    self.save_scene()

class Arducopter(BaseMetadata):
  dbname = 'arducopter'
  description = 'Arducopter GPS metadata'
  meta_name = 'Arducopter'

  def run(self):
    from vsi.iglob import glob

    from .tools import load_arducopter_metadata

    self.task.update_state(state='Processing', meta={'stage':'metadata'})

    metadata_filename = glob(os.path.join(self.ingest_dir, 
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

    metadata = load_arducopter_metadata(metadata_filename)
    
    #determine the origin via average
    origin_xyz = np.mean(np.array(map(lambda x:x.llh_xyz, metadata)), 0)

    self.parse_json(srid=7428, date=date, time_of_day=time_of_day, 
                    origin_xyz=origin_xyz)

    matching_attributes = match_attributes(self.image_collection.images.all(), 
                                           self.json_config)

    for meta in metadata:
      try:
        img = self.image_collection.images.get(
            name__icontains='Frame %s' % meta.filename)
        k = np.eye(3)
        k[0,2] = img.imageWidth/2
        k[1,2] = img.imageHeight/2
        r = np.eye(3)
        t = [0, 0, 0]
        origin = meta.llh_xyz
        save_krt(self.task.request.id, img, k, r, t, origin, srid=self.srid,
                 attributes=matching_attributes.get(img.original_filename, {}))
      except Exception as e:
        logger.warning('%s', e)
        logger.error('Could not match metadata entry for %s' % meta.filename)


    self.save_scene()

class Clif(BaseMetadata):
  dbname='clif'
  description='Columbus Large Image Format Metadata'
  meta_name='CLIF'

  CLIF_DATA = {1.0: {'width':2672, 'height':4016, 
                   'pixel_format':'b', 'dtype':np.uint8,
                   'altitude_conversion':0.3048,
                   'bands':1}}
  CLIF_VERSION = 1.0

  def run(self):
    from vsi.iglob import glob

    from .tools import split_clif

    self.task.update_state(state='Processing', meta={'stage':'metadata'})

    metadata_filenames = glob(os.path.join(self.ingest_dir, '*.txt'), False)
    metadata_filenames = sorted(metadata_filenames, key=lambda s:s.lower())
    metadata_basenames = map(lambda x:os.path.basename(x).lower(), 
                             metadata_filenames)

    date = ''
    time_of_day = ''
    for metadata_filename in metadata_filenames:
      #Loop through until one succeeds
      try:
        with open(metadata_filename, 'r') as fid:
          data = fid.readline().split(',')
        imu_time = float(data[6])
        imu_week = int(data[7])
        timestamp = datetime(1980, 1, 6) + timedelta(weeks=imu_week,
                                                     seconds=imu_time)
        date = '%04d-%02d-%02d' % (timestamp.year, timestamp.month, 
                                   timestamp.day)
        time_of_day = '%02d:%02d:%02d.%06d' % (timestamp.hour, 
                                               timestamp.minute, 
                                               timestamp.second,
                                               timestamp.microsecond)
        break #Break on first success
      except:
        pass

    #Kinda inefficient, kinda don't care
    llhs_xyz=[]
    for metadata_filename in metadata_filenames:
      with open(metadata_filename, 'r') as fid:
        metadata = fid.readline().split(',')

      llh_xyz = [float(metadata[4]), float(metadata[3]), 
          float(metadata[5])*\
          Clif.CLIF_DATA[self.CLIF_VERSION]['altitude_conversion']]
      llhs_xyz.append(llh_xyz)

    origin_xyz = np.mean(np.array(llhs_xyz), 0)

    self.parse_json(date=date, time_of_day=time_of_day, origin_xyz=origin_xyz)

    #Integrate with parse_json OR the itf file. VDL downloads do NOT have this
    #So I'll go with nope.
    pixel_format = Clif.CLIF_DATA[self.CLIF_VERSION]['pixel_format']
    width = Clif.CLIF_DATA[self.CLIF_VERSION]['width']
    height = Clif.CLIF_DATA[self.CLIF_VERSION]['height']
    bands = Clif.CLIF_DATA[self.CLIF_VERSION]['bands']


    matching_attributes = match_attributes(self.image_collection.images.all(), 
                                           self.json_config)

    for image in self.image_collection.images.all():
      filename = image.original_filename
      metadata_filename_desired = split_clif(filename)
      metadata_filename_desired = '%06d-%s.txt' % (0, metadata_filename_desired[2])

      try:
        metadata_index = metadata_basenames.index(metadata_filename_desired)
        metadata_filename = metadata_filenames[metadata_index]

        with open(metadata_filename, 'r') as fid:
          metadata = fid.readline().split(',')

        k = np.eye(3)
        k[0,2] = image.imageWidth/2
        k[1,2] = image.imageHeight/2
        r = np.eye(3)
        t = [0, 0, 0]
        origin = llhs_xyz[metadata_index]
        save_krt(self.task.request.id, image, k, r, t, origin, srid=self.srid,
                 attributes=matching_attributes.get(image.original_filename, {}))
      except Exception as e:
        pass

    self.save_scene()

class AngelFire(BaseMetadata):
  dbname='angelfire'
  description='Angel Fire'
  meta_name=description

  AF_DATA = {1.0: {'altitude_conversion':0.3048}}
  AF_VERSION = 1.0

  def run(self):
    from vsi.iglob import glob

    self.task.update_state(state='Processing', meta={'stage':'metadata'})

    metadata_filenames = glob(os.path.join(self.ingest_dir, '*.pos'), False)
    metadata_filenames = sorted(metadata_filenames, key=lambda s:s.lower())
    metadata_basenames = map(lambda x:os.path.split(x)[-1].lower(), 
                             metadata_filenames)

    for metadata_filename in metadata_filenames:
#      try:
        timestamp = os.path.split(metadata_filenames[0])[1].split('-')[0]
        date = timestamp[0:4]+'-'+timestamp[4:6]+'-'+timestamp[6:8]
        time_of_day = timestamp[8:10]+':'+timestamp[10:12]+':'+timestamp[12:14]
        break #on first success
#      except:
        pass

    llhs_xyz=[]
    for metadata_filename in metadata_filenames:
      with open(metadata_filename, 'r') as fid:
        metadata = fid.readline().split(',')

      llh_xyz = [float(metadata[5]), float(metadata[4]), 
                 float(metadata[6]) \
                 *AngelFire.AF_DATA[self.AF_VERSION]['altitude_conversion']]
      llhs_xyz.append(llh_xyz)

    origin_xyz = np.mean(np.array(llhs_xyz), 0)

    self.parse_json(date=date, time_of_day=time_of_day, origin_xyz=origin_xyz)

    matching_attributes = match_attributes(self.image_collection.images.all(), 
                                           self.json_config)


    for image in self.image_collection.images.all():
      filename = image.original_filename
      metadata_filename_desired = (os.path.splitext(
          os.path.split(filename)[-1])[0][0:-6]+'00-VIS.pos').lower()

      try:
        metadata_index = metadata_basenames.index(metadata_filename_desired)
        metadata_filename = metadata_filenames[metadata_index]

        k = np.eye(3)
        k[0,2] = image.imageWidth/2
        k[1,2] = image.imageHeight/2
        r = np.eye(3)
        t = [0, 0, 0]
        origin = llhs_xyz[metadata_index]
        save_krt(self.task.request.id, image, k, r, t, origin, srid=self.srid,
                 attributes=matching_attributes.get(image.original_filename, {}))
      except Exception as e:
        pass

    self.save_scene()

class NoMetadata(BaseMetadata):
  dbname='nometa'
  description='No Metadata'
  meta_name=''

  def run(self):
    #You add the rest to create your brand new parser! That's it!
    self.task.update_state(state='Processing', meta={'stage':'metadata'})
    self.parse_json() #Set some defaults for parsing config file
    matching_attributes = match_attributes(self.image_collection.images.all(), 
                                           self.json_config)

    k = np.eye(3)
    r = np.eye(3)
    t = np.zeros(3)
    origin = [0,0,0]
    for image in self.image_collection.images.all():
      k[0,2] = image.imageWidth/2
      k[1,2] = image.imageHeight/2
      save_krt(self.task.request.id, image, k, r, t, origin, srid=self.srid,
               attributes=matching_attributes.get(image.original_filename, {}))
    self.save_scene()
    self.image_collection.scene.geolocated = False
    self.image_collection.scene.save()

class JpegExif(BaseMetadata):
  dbname='jpegexif'
  description='JPEG Exif'
  meta_name=description

  def run(self):
    from vsi.io.image import PilReader

    from vsi.iglob import glob
    from vsi.tools import Try

    from .tools import exif_date_time_parse

    self.task.update_state(state='Processing', meta={'stage':'metadata'})

    self.parse_json()

    gpsList=[]
    gpsList2=[]

    k = np.eye(3)
    r = np.eye(3)
    t = [0, 0, 0]

    matching_attributes = match_attributes(self.image_collection.images.all(), 
                                           self.json_config)

    for image in self.image_collection.images.all():
      filename = os.path.join(self.ingest_dir, image.original_filename)
      
      try:
        img = PilReader(filename, True)

        with Try():
          exifTags = img.object._getexif()
          gps = exifTags[34853]

        if self.date=='':
          with Try():
            try:
              self.date, self.time_of_day = exif_date_time_parse(
                  exifTags[36867])
            except:
              try:
                self.date, self.time_of_day = exif_date_time_parse(
                    exifTags[306])
              except:
                try:
                  self.date, self.time_of_day = exif_date_time_parse(
                      exifTags[36868])
                except:
                  pass


        try:
          latitude = float(gps[2][0][0])/gps[2][0][1] + \
                     float(gps[2][1][0])/gps[2][1][1]/60.0 + \
                     float(gps[2][2][0])/gps[2][2][1]/3600.0
          if gps[1] == 'N':
            pass
          elif  gps[1] == 'S':
            latitude *= -1
          else:
            latitude *= 0
        except:
          latitude = 0
          
        try:
          longitude = float(gps[4][0][0])/gps[4][0][1] + \
                      float(gps[4][1][0])/gps[4][1][1]/60.0 + \
                      float(gps[4][2][0])/gps[4][2][1]/3600.0
          if gps[3] == 'W':
            longitude *= -1
          elif  gps[3] == 'E':
            pass
          else:
            longitude *= 0
        except:
          longitude = 0
          
        try:
          #if positive, assume no flag 5 == positive
          if 5 not in gps or gps[5] == '\x00':
            altitude = float(gps[6][0])/gps[6][1]
          else: #negative
            altitude = float(gps[6][0])/gps[6][1]
        except:
          altitude = 0
        
        #Untested code, because I don't have images with this tag!
        try:
          if gps[18] == 'WGS-84': #http://www.cipa.jp/std/documents/e/DC-008-2010_E.pdf
            self.srid = 4326
          elif gps[18] == 'EGM96': #I'm guessing here?
            self.srid = 7428  #EGM 96
        except:
          pass

        origin = [longitude, latitude, altitude]
        if not any(np.array(origin[0:2]) == 0):
          gpsList.append(origin)
        gpsList2.append(origin)

        k[0,2] = image.imageWidth/2
        k[1,2] = image.imageHeight/2
        save_krt(self.task.request.id, image, k, r, t, origin, srid=self.srid,
                 attributes=matching_attributes.get(image.original_filename, {}))
      except Exception as e:
        pass

    logger.error(gpsList)
    logger.error(gpsList2)

    try:
      self.origin_xyz = np.mean(np.array(gpsList), 0)
      if len(averageGps) != 3:
        raise ValueError
    except:
      self.origin_xyz = np.mean(np.array(gpsList2), 0)

    logger.error(self.origin_xyz)

    self.save_scene()


### EXAMPLE ###

class Example(BaseMetadata):
  dbname='example'
  description='This is just an example'
  meta_name='Example'

  def run(self):
    #You add the rest to create your brand new parser! That's it!
    self.task.update_state(state='Processing', meta={'stage':'metadata'})
    self.parse_json(srid=5467) #Set some defaults for parsing config file
    matching_attributes = match_attributes(self.image_collection.images.all(), 
                                           self.json_config)
    for image in self.image_collection.images.all():
      save_krt(self.task.request.id, image, k, r, t, origin, srid=self.srid,
               attributes=matching_attributes.get(image.original_filename, {}))
    self.save_scene()

#I haven't yet come up with a clever way of not repeating myself and not 
#needing this. The function here is NEVER called, so might as well make it pass
#The name of the function is used in the celery task registry
#this would ACTUALLY register the Example class, so it's commented out
#@Example.task
#def example():
#  pass


#This pattern handles the class method tasks caveats, and since
#This is in a module, it would have been ugly and a pain
@Krt.task
def krt():
  pass

@Arducopter.task
def arducopter():
  pass

@Clif.task
def clif():
  pass

@AngelFire.task
def af():
  pass

@NoMetadata.task
def nometa():
  pass

@JpegExif.task
def jpegexif():
  pass
