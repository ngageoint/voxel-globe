from voxel_globe.common_tasks import app, VipTask
import voxel_globe.meta.models
from vsi.iglob import glob
import os
from voxel_globe.tools.subprocessbg import Popen
from os import environ as env
import urllib

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__);

@app.task(base=VipTask, bind=True)
def ingest_data(self, uploadSession_id, imageDir):
  ''' task for the ingest route, to ingest the data an upload sessions points to '''
  import voxel_globe.ingest.models as IngestModels
  import numpy
  from voxel_globe.tools.camera import save_krt

  uploadSession = IngestModels.UploadSession.objects.get(id=uploadSession_id);
  #directories = uploadSession.directory.all();
  #imageDirectory = directories.filter(name='image')
  #metaDirectory = directories.filter(name='meta')

  imageCollection = voxel_globe.meta.models.ImageCollection.create(name="Generic Upload %s (%s)" % (uploadSession.name, uploadSession_id), service_id = self.request.id);
  imageCollection.save();

  r = numpy.eye(3);
  t = [0, 0, 0];

  gpsList = []
  gpsList2 = []

  for d in glob(os.path.join(imageDir, '*'+os.path.sep), False):
    files = glob(os.path.join(d, '*'), False);
    files.sort()
    for f in files:
      self.update_state(state='PROCESSING', 
                        meta={'stage':'File %s of %d' % (f, len(files))})
      zoomifyName = f[:-4] + '_zoomify'
      pid = Popen(['vips', 'dzsave', f, zoomifyName, '--layout', 'zoomify'])
      pid.wait();

      #convert the slashes to URL slashes 
      relFilePath = urllib.pathname2url(os.path.relpath(f, env['VIP_IMAGE_SERVER_ROOT']));
      basename = os.path.split(f)[-1]
      relZoomPath = urllib.pathname2url(os.path.relpath(zoomifyName, env['VIP_IMAGE_SERVER_ROOT']));

      with open(f, 'rb') as fid:
        magic = fid.read(4)
        
      image_info = {}
      if magic == '49492A00'.decode('hex') or \
         magic == '4D4D002A'.decode('hex'):
        logger.debug('Tifffile: %s', f)
        from tifffile import TiffFile

        with TiffFile(f) as image:
          if image.pages[0].dtype == 's':
            image_info['dtype'] = numpy.dtype('S')
          else:
            image_info['dtype'] = numpy.dtype(image.pages[0].dtype)
          image_info['bps'] = image.pages[0].bits_per_sample
          image_info['height'] = image.pages[0].shape[0] #Yep, y,x,z order
          image_info['width'] = image.pages[0].shape[1]
          try:
            image_info['bands'] = image.pages[0].shape[2]
          except IndexError:
            image_info['bands'] = 1
      else:
        logger.debug('Pil: %s', f)
        from PIL import Image
        
        with Image.open(f) as image:
          #The getmode* commands do not give you the REAL datatypes. I need the
          #REAL (numpy in this case) bps, not some random PIL designation
          image_info['dtype'] = numpy.dtype(Image._MODE_CONV[image.mode][0])
          #probably doesn't work well for bool... Oh well
          image_info['bps'] = image_info['dtype'].itemsize*8
          image_info['width'] = image.size[0] #Yep, x,y order
          image_info['height'] = image.size[1]
          image_info['bands'] = Image.getmodebands(image.mode)

      img = voxel_globe.meta.models.Image.create(
                             name="Generic Upload %s (%s) Frame %s" % (uploadSession.name, uploadSession_id, basename), 
                             imageWidth=image_info['width'], 
                             imageHeight=image_info['height'], 
                             numberColorBands=image_info['bands'],
                             pixelFormat=image_info['dtype'].char,
                             fileFormat='zoom',
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
      
      origin = [0,0,0];
      logger.debug('Origin is: %s' % origin)

      k = numpy.eye(3);
      k[0,2] = image_info['width']/2;
      k[1,2] = image_info['height']/2;      
      save_krt(self.request.id, img, k, r, t, origin);

  voxel_globe.meta.models.Scene.create(name="Generic origin %s (%s)" % (uploadSession.name, uploadSession_id), 
                                       service_id = self.request.id,
                                       geolocated=False,
                                       origin='POINT(%0.12f %0.12f %0.12f)' % \
                                       (0,0,0)).save()
  uploadSession.delete()
ingest_data.dbname='no_metadata'
ingest_data.description="Generic Images with no metadata"