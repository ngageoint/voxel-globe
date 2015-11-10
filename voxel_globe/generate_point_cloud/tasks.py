from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

import os

@shared_task(base=VipTask, bind=True)
def generate_point_cloud(self, voxel_world_id, prob=0.5, history=None):
  from glob import glob
  import json

  import numpy as np

  from boxm2_adaptor import load_cpp, render_depth, cast_3d_point, \
                            cast_3d_point_pass2, write_cache, \
                            create_stream_cache
  from boxm2_scene_adaptor import boxm2_scene_adaptor
  from vpgl_adaptor import create_perspective_camera_krt, persp2gen, \
                           compute_direction_covariance
  from boxm2_mesh_adaptor import batch_compute_3d_points, gen_error_point_cloud

  from vsi.tools.redirect import Redirect, Logger as LoggerWrapper

  import voxel_globe.tools
  import voxel_globe.meta.models as models
  from voxel_globe.tools.camera import get_krt

  with Redirect(stdout_c=LoggerWrapper(logger, lvl=logging.INFO),
                stderr_c=LoggerWrapper(logger, lvl=logging.WARNING)):


    self.update_state(state='SETUP', meta={'pid':os.getpid()})

    voxel_world = models.VoxelWorld.objects.get(id=voxel_world_id)
    service_inputs = json.loads(voxel_world.service.inputs)
    image_collection = models.ImageCollection.objects.get(
        id=service_inputs[0][0])
    images = image_collection.images.all()
    #images = images[::2]
    images = images[::20]
    scene = models.Scene.objects.get(id=service_inputs[0][1])

    voxel_world_dir = voxel_world.directory
    
    scene_filename = os.path.join(voxel_world_dir, 'scene.xml')

    opencl_device = os.environ['VIP_OPENCL_DEVICE']
    scene_gpu = boxm2_scene_adaptor(scene_filename, opencl_device)
    scene_cpp = boxm2_scene_adaptor(scene_filename, 'cpp')
    
    type_id_fname = "type_names_list.txt"
    image_id_fname = "image_list.txt"
    
    std_dev_angle = 0.1
    cov_c_path = 'cov_c.txt'
    cov_c = 0*np.eye(3)*0.8**2

    with voxel_globe.tools.task_dir('generate_point_cloud', cd=True) \
         as processing_dir:
      np.savetxt(cov_c_path, cov_c)

      for index, image in enumerate(images):
        self.update_state(state='PROCESSING', 
                          meta={'stage':'casting', 'image':index+1, 
                                'total':len(images)})

        k,r,t,o = get_krt(image.history(history))

        perspective_camera = create_perspective_camera_krt(k, r, t)

        (depth_image, variance_image, _) = render_depth(scene_gpu.scene, 
              scene_gpu.opencl_cache, perspective_camera, 
              image.imageWidth, image.imageHeight, 
              scene_gpu.device)

        cov_v_path = 'cov_%06d.txt' % index
        appearance_model = 'image_%06d' % index

        generic_camera = persp2gen(perspective_camera, image.imageWidth, 
                                   image.imageHeight)

        compute_direction_covariance(perspective_camera, std_dev_angle, 
                                     cov_v_path)

        cast_3d_point(scene_cpp.scene,scene_cpp.cpu_cache,perspective_camera,
                      generic_camera,depth_image,variance_image,appearance_model)
        cast_3d_point_pass2(scene_cpp.scene,scene_cpp.cpu_cache,generic_camera,
                            appearance_model,cov_c_path,cov_v_path)

        write_cache(scene_cpp.cpu_cache, 1)

      self.update_state(state='PROCESSING', 
                          meta={'stage':'compute error'})

      with open(image_id_fname, 'w') as fid:
        print >>fid, len(images)
        for index, image in enumerate(images):
          print >>fid, 'image_%06d' % (index)
      
      with open(type_id_fname,"w") as fid:
        print >>fid, 2
        print >>fid, "boxm2_point"
        print >>fid, "boxm2_covariance"

      mem=3.0
      stream_cache = create_stream_cache(scene_cpp.scene, type_id_fname, 
                                         image_id_fname, mem)
      batch_compute_3d_points(scene_cpp.scene, scene_cpp.cpu_cache, stream_cache)

      self.update_state(state='EXPORTING', 
                          meta={'stage':'ply'})

      with voxel_globe.tools.storage_dir('generate_point_cloud') \
           as storage_dir:
        gen_error_point_cloud(scene_cpp.scene, scene_cpp.cpu_cache, 
          os.path.join(storage_dir, 'error.ply'), 0.5, True)

      models.PointCloud.create(name='%s point cloud' % image_collection.name,
        service_id=self.request.id, origin=voxel_world.origin,
        directory=storage_dir).save()

      voxel_files = lambda x: glob(os.path.join(voxel_world_dir, x))
      cleanup_files = []
      cleanup_files += voxel_files('boxm2_covariance_*.bin')
      cleanup_files += voxel_files('boxm2_point_*.bin')
      cleanup_files += voxel_files('float16_image_*.bin')
      for cleanup_file in cleanup_files:
        os.remove(cleanup_file)
