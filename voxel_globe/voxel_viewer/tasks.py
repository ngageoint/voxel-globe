from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

import os

@shared_task(base=VipTask, bind=True)
def run_point_cloud(self, voxel_world_id, threshold, history=None):
  import voxel_globe.tools

  import voxel_globe.meta.models as models

  import boxm2_adaptor
  import boxm2_mesh_adaptor

  from plyfile import PlyData

  voxel_world = models.VoxelWorld.objects.get(id=voxel_world_id).history(history)

  with voxel_globe.tools.task_dir('voxel_viewer') as processing_dir:
    scene_path = os.path.join(voxel_world.voxel_world_dir, 'scene.xml')
    scene,cache = boxm2_adaptor.load_cpp(scene_path)
    ply_filename = os.path.join(processing_dir, 'model.ply')
    boxm2_mesh_adaptor.gen_color_point_cloud(scene, cache, ply_filename, 0.5, "")

    ply = PlyData.read(str(ply_filename))

    return ply.elements[0].data

@shared_task(base=VipTask, bind=True)
def ingest_point_cloud(self, voxel_world_id, threshold=0, number_points=None, history=None):
  import voxel_globe.tools
  from .tools import get_point_cloud

  points = get_point_cloud(voxel_world_id)

  if number_points:
    pass
  
  for x in xrange(len(points['latitude'])):
    point = 'SRID=4326;POINT(%0.18f %018f %0.18f)' % \
        (points['longitude'][x],points['latitude'][x],points['altitude'][x])
    voxel_globe.meta.models.ControlPoint.create(
        name='Point Cloud point %d[%d]' % (x, voxel_world_id), 
        description='Temp',
        point=point, apparentPoint=point, service_id=self.request.id).save()

