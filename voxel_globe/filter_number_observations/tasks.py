import os
from os import environ as env

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

from voxel_globe.common_tasks import shared_task, VipTask

@shared_task(base=VipTask, bind=True)
def filter_number_observations(self, voxel_world_id, mean_multiplier=3.0):
  from boxm2_scene_adaptor import boxm2_scene_adaptor

  import voxel_globe.meta.models as models

  voxel_world = models.VoxelWorld.objects.get(id=voxel_world_id)
  scene_file = os.path.join(voxel_world.directory, 'scene.xml')

  scene = boxm2_scene_adaptor(scene_file, env['VIP_OPENCL_DEVICE'])
  self.update_state(state='PROCESSING', meta={'stage':'remove low observers'})
  scene.remove_low_nobs(mean_multiplier)
  self.update_state(state='SAVING')
  scene.write_cache()