from voxel_globe.common_tasks import shared_task, VipTask

import os
from vsi.iglob import glob
import voxel_globe.meta.models
from os import environ as env
import urllib
import numpy as np

from voxel_globe.tools.subprocessbg import Popen

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__);

CLIF_DATA = {1.0: {'width':2672, 'height':4016, 
                   'pixel_format':'b', 'dtype':np.uint8,
                   'altitude_conversion':0.3048,
                   'bands':1}}
CLIF_VERSION = 1.0

@shared_task(base=VipTask, bind=True)
def ingest_data(self, uploadSession_id, imageDir):
  ''' task for the ingest route, to ingest the data an upload sessions points 
      to '''
  import voxel_globe.ingest.models as IngestModels
  from voxel_globe.tools.camera import save_krt
  from PIL import Image
  from datetime import datetime, timedelta
  from .tools import split_clif


  uploadSession = IngestModels.UploadSession.objects.get(id=uploadSession_id);

  metadataFilenames = glob(os.path.join(imageDir, '*.txt'), False);
  metadataFilenames = sorted(metadataFilenames, key=lambda s:s.lower())
  metadataBasenames = map(lambda x:os.path.basename(x).lower(), metadataFilenames)

  #In case none of them  succeeded...
  date = 'NYA'
  timeOfDay = 'NYA'

  for metadata_filename in metadataFilenames:
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
      timeOfDay = '%02d:%02d:%02d.%06d' % (timestamp.hour, timestamp.minute, 
                                           timestamp.second,
                                           timestamp.microsecond)
      break #Break on first success
    except:
      pass

  imageCollection = voxel_globe.meta.models.ImageCollection.create(
      name="CLIF Upload %s %s %s (%s)" % (uploadSession.name, date, 
                                          timeOfDay, uploadSession_id), 
                                          service_id = self.request.id);
  imageCollection.save();

  llhs_xyz = []

  #for d in glob(os.path.join(imageDir, '*'+os.path.sep), False):
  if 1:
    files = glob(os.path.join(imageDir, '*'+os.extsep+'raw'), False);
    files.sort()
    for index,f in enumerate(files):
      self.update_state(state='PROCESSING', 
                        meta={'stage':'File %s (%d of %d)' % (f, index+1, len(files))})
      logger.debug('Processing %s (%d of %d)', f, index+1, len(files))

      basename = os.path.basename(f)
      img_filename = os.extsep.join([os.path.splitext(f)[0], 'png'])

      with open(f, 'rb') as fid:
        data = fid.read();
      img = np.fromstring(data, 
                          dtype=CLIF_DATA[CLIF_VERSION]['dtype']).reshape(
          (CLIF_DATA[CLIF_VERSION]['width'], 
           CLIF_DATA[CLIF_VERSION]['height'])).T
      img2 = Image.fromarray(img)
      img2.save(img_filename)

      zoomifyName = os.path.splitext(f)[0] + '_zoomify'
      pid = Popen(['vips', 'dzsave', img_filename, zoomifyName, '--layout', 'zoomify'])
      pid.wait();

      #convert the slashes to URL slashes 
      relFilePath = urllib.pathname2url(os.path.relpath(img_filename, env['VIP_IMAGE_SERVER_ROOT']));
      basename = os.path.split(f)[-1]
      relZoomPath = urllib.pathname2url(os.path.relpath(zoomifyName, env['VIP_IMAGE_SERVER_ROOT']));

      pixel_format = CLIF_DATA[CLIF_VERSION]['pixel_format']
      width = CLIF_DATA[CLIF_VERSION]['width']
      height = CLIF_DATA[CLIF_VERSION]['height']
      bands = CLIF_DATA[CLIF_VERSION]['bands']

      img = voxel_globe.meta.models.Image.create(
                             name="CLIF Upload %s (%s) Frame %s" % (uploadSession.name, uploadSession_id, basename), 
                             imageWidth=width, imageHeight=height, 
                             numberColorBands=bands, pixelFormat=pixel_format, fileFormat='zoom', 
                             imageUrl='%s://%s:%s/%s/%s/' % (env['VIP_IMAGE_SERVER_PROTOCOL'], 
                                                             env['VIP_IMAGE_SERVER_HOST'], 
                                                             env['VIP_IMAGE_SERVER_PORT'], 
                                                             env['VIP_IMAGE_SERVER_URL_PATH'], 
                                                             relZoomPath),
                             originalImageUrl='%s://%s:%s/%s/%s' % (env['VIP_IMAGE_SERVER_PROTOCOL'], 
                                                                    env['VIP_IMAGE_SERVER_HOST'], 
                                                                    env['VIP_IMAGE_SERVER_PORT'], 
                                                                    env['VIP_IMAGE_SERVER_URL_PATH'], 
                                                                    relFilePath),
                             service_id = self.request.id);
      img.save();
     
      imageCollection.images.add(img);

      metadata_filename_desired = split_clif(f)
      metadata_filename_desired = '%06d-%s.txt' % (0, metadata_filename_desired[2])
      if 1:
#      try:
        metadata_index = metadataBasenames.index(metadata_filename_desired)
        metadata_filename = metadataFilenames[metadata_index]
        with open(metadata_filename, 'r') as fid:
          metadata = fid.readline().split(',')

        llh_xyz = [float(metadata[4]), float(metadata[3]), 
            float(metadata[5])*CLIF_DATA[CLIF_VERSION]['altitude_conversion']]
        llhs_xyz.append(llh_xyz)
        k = np.eye(3);
        k[0,2] = width/2;
        k[1,2] = height/2;      
        r = np.eye(3);
        t = [0, 0, 0];
        origin = llh_xyz;
        save_krt(self.request.id, img, k, r, t, origin, srid=4326);
#      except Exception as e:
        pass

  averageGps = np.mean(np.array(llhs_xyz), 0);
  
  voxel_globe.meta.models.Scene.create(name="CLIF origin %s (%s)" % (uploadSession.name, uploadSession_id), 
                                       service_id = self.request.id,
                                       origin='SRID=%d;POINT(%0.12f %0.12f %0.12f)' % \
                                       (4326, averageGps[0], averageGps[1], averageGps[2])).save()
  uploadSession.delete()

ingest_data.dbname="clif"
ingest_data.description = "Columbus Large Image Format"
