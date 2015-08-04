from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

import os

@shared_task(base=VipTask, bind=True)
def run_point_clound(self, voxel_world_id, threshold, history=None):
  import voxel_globe.tools

  import voxel_globe.meta.models as models

  import boxm2_adaptor
  import boxm2_mesh_adaptor

  from plyfile import PlyData

  voxel_world = models.VoxelWorld.objects.get(id=voxel_world_id).history(history)

  with voxel_globe.tools.taskDir() as processing_dir:
    scene_path = os.path.join(voxel_world.voxel_world_dir, 'scene.xml')
    scene,cache = boxm2_adaptor.load_cpp(scene_path)
    ply_filename = os.path.join(processing_dir, 'model.ply')
    boxm2_mesh_adaptor.gen_color_point_cloud(scene, cache, ply_filename, 0.5, "")

    ply = PlyData.read(str(ply_filename))

    return ply.elements[0].data