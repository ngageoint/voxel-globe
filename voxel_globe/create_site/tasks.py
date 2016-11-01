import os
from os import environ as env

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

from voxel_globe.common_tasks import shared_task, VipTask

@shared_task(base=VipTask, bind=True)
def create_site(self, sattel_site_id):
  import voxel_globe.meta.models as models
  from .tools import PlanetClient
  import geojson
  import shutil
  import voxel_globe.tools.voxel_dir as voxel_dir
  from datetime import datetime
  import pytz
  import json
  from glob import glob
  import zipfile
  import tifffile
  import numpy as np
  from PIL import Image, ImageOps

  import voxel_globe.ingest.models
  from voxel_globe.tools.camera import save_rpc
  from vsi.io.image import imread
  import voxel_globe.ingest.payload.tools as payload_tools

  site = models.SattelSite.objects.get(id=sattel_site_id)

  w = site.bbox_min[0]
  s = site.bbox_min[1]
  e = site.bbox_max[0]
  n = site.bbox_max[1]

  key=env['VIP_PLANET_LABS_API_KEY']

  # search dates
  start = datetime(year=2016, month=1, day=1, tzinfo=pytz.utc)
  stop = datetime(year=2017, month=1, day=1, tzinfo=pytz.utc)

  cloudmax=50

  platforms = ('planetscope')

  coords = [[(w,n),(e,n),(e,s),(w,s),(w,n)]]
  geometry = geojson.Polygon(coords)

  query = {
    "start": start,
    "stop": stop,
    "aoi": geometry,    
    "cloudmax": cloudmax,
    "platforms": platforms,
  }

  with voxel_dir.storage_dir('external_download') as processing_dir, PlanetClient(key) as client:
    # count available images
    # (Planet can return a huge list of images, spanning all images
    # in their database.  Check the count before proceeding)
    self.update_state(state='QUERYING')
    nbr = client.countImages(query=query)
    logger.debug(query)
    logger.info("Number of images: %d",nbr)

    scenes = client.describeImages(query=query)
    #logger.debug(json.dumps(scenes, indent=2))


#    thumbs = client.downloadThumbnails(scenes,
#        folder=processing_dir,type='unrectified',
#        size='md',format='png')
#    self.update_state(state='DOWNLOADING', meta={"type":"images",
#                                                 "total":nbr})

    image_set = models.ImageSet(name="Site: %s" % site.name,
                                service_id=self.request.id)
    image_set.save()
    camera_set = models.CameraSet(name="Site: %s" % site.name,
                                  images=image_set,
                                  service_id=self.request.id)
    camera_set.save()

    site.image_set = image_set
    site.camera_set = camera_set
    site.save()

    for idx,scene in enumerate(scenes):

      # update 
      self.update_state(state='DOWNLOADING', meta={"type":"Images",
                                                 "total":nbr,"index":idx,
                                                 "site_name": site.name})

      # download one scene to ZIP
      files = client.downloadImages(scene,
          folder=processing_dir,type='unrectified.zip')
      filezip = files[0]
      logger.debug(filezip)

      # unzip file to isolated folder
      name,ext = os.path.splitext(os.path.basename(filezip))
      logger.debug(name)
      zip_dir = os.path.join(processing_dir,name)
      logger.debug(zip_dir)

      with zipfile.ZipFile(filezip, 'r') as z:
        z.extractall(zip_dir)
      os.remove(filezip)

      logger.debug(glob(os.path.join(zip_dir, '*/')))
      dir_name = glob(os.path.join(zip_dir, '*/'))[0]
      #for dir_name in glob(os.path.join(zip_dir, '*/')):
      logger.debug(dir_name)
      rpc_name = glob(os.path.join(dir_name, '*_RPC.TXT'))[0]
      image_name = glob(os.path.join(dir_name, '*.tif'))[0]

      #juggle files
      image_name = payload_tools.move_to_sha256(image_name)
      rpc_name_new = os.path.join(os.path.dirname(image_name), 
                                  os.path.basename(rpc_name))
      shutil.move(rpc_name, rpc_name_new)
      rpc_name = rpc_name_new
      del rpc_name_new

      scaled_imagename = os.path.join(os.path.dirname(image_name), 
                                      'scaled_'+os.path.basename(image_name))

      img = imread(image_name)
      pixel_format = np.sctype2char(img.dtype())

      #Make viewable image
      img2 = img.raster()[:,:,0:3]
      img2 = img2.astype(np.float32)/np.amax(img2.reshape(-1, 3), 
                                             axis=0).reshape(1,1,3)
      #Divide by max for each color
      img2 = Image.fromarray(np.uint8(img2*255))
      #Convert to uint8 for PIL :(
      img2 = ImageOps.autocontrast(img2, cutoff=1)
      #autocontrast
      img2.save(scaled_imagename)
      del img2

      attributes={}
      if os.path.basename(image_name) == scene['id']+'.tif':
        attributes['planet_rest_response'] = scene

      image = models.Image(
          name="Planet %s" % (os.path.basename(image_name),),
          image_width=img.shape()[1], image_height=img.shape()[0],
          number_bands=img.bands(), pixel_format=pixel_format, file_format='zoom',
          service_id=self.request.id)
      image.filename_path=image_name
      image.attributes=attributes
      image.save()
      image_set.images.add(image)
      payload_tools.zoomify_image(scaled_imagename, image.zoomify_path)
      os.remove(scaled_imagename)


      rpc = models.RpcCamera(name=os.path.basename(image_name),
                             rpc_path=rpc_name, image=image)
      rpc.save()
      camera_set.cameras.add(rpc)


    return {"site_name" : site.name}