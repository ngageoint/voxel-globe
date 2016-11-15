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
  import voxel_globe.tools
  from vsi.tools.dir_util import copytree

  voxel_world = models.VoxelWorld.objects.get(id=voxel_world_id)

  with voxel_globe.tools.storage_dir('voxel_world') as storage_dir:
    copytree(voxel_world.directory, storage_dir)
    voxel_world.id = None
    voxel_world.directory = storage_dir
    voxel_world.name = 'Filtered at %d %s' % (mean_multiplier,
                                              voxel_world.name)
    voxel_world.service_id = self.request.id
    voxel_world.save()
    scene_file = os.path.join(storage_dir, 'scene.xml')

  scene = boxm2_scene_adaptor(scene_file, env['VIP_OPENCL_DEVICE'])
  self.update_state(state='PROCESSING', meta={'stage':'remove low observers'})
  scene.remove_low_nobs(mean_multiplier)
  self.update_state(state='SAVING')
  scene.write_cache()