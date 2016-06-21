import os
from os import environ as env

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

from voxel_globe.common_tasks import shared_task, VipTask

@shared_task(base=VipTask, bind=True)
def create_site(self, sattel_site_id):
  logger.critical('dummy task for sattel create site: %d', sattel_site_id)
  pass
