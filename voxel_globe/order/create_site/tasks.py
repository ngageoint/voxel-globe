import os
from os import environ as env

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

from voxel_globe.common_tasks import shared_task, VipTask

@shared_task(base=VipTask, bind=True)
def create_site(self, sattel_site_id):
  import voxel_globe.meta.models as models
  from .planetv0 import Client
  import geojson
  import voxel_globe.tools.voxel_dir as voxel_dir
  from datetime import datetime
  import pytz
  import json

  site = models.SattelSite.objects.get(id=sattel_site_id)

  w = site.bbox_min[0]
  s = site.bbox_min[1]
  e = site.bbox_max[0]
  n = site.bbox_max[1]

  w = site.bbox_min[1]
  s = site.bbox_min[0]
  e = site.bbox_max[1]
  n = site.bbox_max[0]

  key='ad6a2a72587a48629803d6a29906169a'

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

  with voxel_dir.storage_dir('external_download') as processing_dir, Client(key) as client:
    # count available images
    # (Planet can return a huge list of images, spanning all images
    # in their database.  Check the count before proceeding)
    nbr = client.countImages(query=query)
    logger.debug(query)
    logger.info("Number of images: %d",nbr)

    scenes = client.describeImages(query=query)
    logger.debug(json.dumps(scenes, indent=2))
    
    thumbs = client.downloadThumbnails(scenes,
        folder=processing_dir,type='unrectified',
        size='md',format='png')

    files = client.downloadImages(scenes,
        folder=processing_dir,type='unrectified.zip')
