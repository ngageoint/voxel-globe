import os
from os import environ as env

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

from voxel_globe.common_tasks import shared_task, VipTask


@shared_task(base=VipTask, bind=True)
def generate_error_point_cloud(self, voxel_world_id, prob=0.5, history=None):
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

    with voxel_globe.tools.task_dir('generate_error_point_cloud', cd=True) \
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

      with voxel_globe.tools.storage_dir('generate_error_point_cloud') \
           as storage_dir:
        gen_error_point_cloud(scene_cpp.scene, scene_cpp.cpu_cache, 
          os.path.join(storage_dir, 'error.ply'), 0.5, True)

        potree_filename = os.path.join(storage_dir, 'potree.ply')
        convert_ply_to_potree(ply_filename, potree_filename)

      with voxel_globe.tools.image_dir('point_cloud') as potree_dir:
        convert_ply_to_potree(ply_filename, potree_dir)

      models.PointCloud.create(name='%s point cloud' % image_collection.name,
        service_id=self.request.id, origin=voxel_world.origin,
        potree_url='%s://%s:%s/%s/point_cloud/%s/cloud.js' % \
          (env['VIP_IMAGE_SERVER_PROTOCOL'], env['VIP_IMAGE_SERVER_HOST'], 
           env['VIP_IMAGE_SERVER_PORT'], env['VIP_IMAGE_SERVER_URL_PATH'], 
           os.path.basename(potree_dir)),
        directory=storage_dir).save()

      voxel_files = lambda x: glob(os.path.join(voxel_world_dir, x))
      cleanup_files = []
      cleanup_files += voxel_files('boxm2_covariance_*.bin')
      cleanup_files += voxel_files('boxm2_point_*.bin')
      cleanup_files += voxel_files('float16_image_*.bin')
      for cleanup_file in cleanup_files:
        os.remove(cleanup_file)

@shared_task(base=VipTask, bind=True)
def generate_threshold_point_cloud(self, voxel_world_id, prob=0.5, 
                                   history=None):
  import json

  import boxm2_adaptor
  import boxm2_mesh_adaptor

  import voxel_globe.tools
  import voxel_globe.meta.models as models

  voxel_world = models.VoxelWorld.objects.get(id=voxel_world_id)
  service_inputs = json.loads(voxel_world.service.inputs)
  image_collection = models.ImageCollection.objects.get(
      id=service_inputs[0][0])

  with voxel_globe.tools.storage_dir('generate_point_cloud', cd=True) \
       as output_dir:
    scene_path = os.path.join(voxel_world.directory, 'scene.xml')
    scene,cache = boxm2_adaptor.load_cpp(scene_path)
    ply_filename = os.path.join(output_dir, 'model.ply')
    boxm2_mesh_adaptor.gen_color_point_cloud(scene, cache, ply_filename, prob, "")

  with voxel_globe.tools.image_dir('point_cloud') as potree_dir:
    convert_ply_to_potree(ply_filename, potree_dir)

  models.PointCloud.create(name='%s threshold point cloud' % image_collection.name,
      service_id=self.request.id, origin=voxel_world.origin,
      potree_url='%s://%s:%s/%s/point_cloud/%s/cloud.js' % \
        (env['VIP_IMAGE_SERVER_PROTOCOL'], env['VIP_IMAGE_SERVER_HOST'], 
         env['VIP_IMAGE_SERVER_PORT'], env['VIP_IMAGE_SERVER_URL_PATH'], 
         os.path.basename(potree_dir)),
      directory=output_dir).save() 

def convert_ply_to_potree(ply_filename, potree_dirname):
  from voxel_globe.tools.subprocessbg import Popen

  potree_ply = os.path.join(potree_dirname, 'potree.ply')

  with open(ply_filename, 'r') as fid_in, open(potree_ply, 'w') as fid_out:
    line = 'None'
    while not line.startswith('end_header') and line != '':
      line = fid_in.readline()
      if line == 'property float prob\n':
        line = 'property float nx\n'
      if line == 'property float le\n':
        line = 'property float ny\n'
      if line == 'property float ce\n':
        line = 'property float nz\n'
      fid_out.write(line)
    chunk = None
    while not chunk == '':
      chunk = fid_in.read(64*1024*1024)
      fid_out.write(chunk)

  pid = Popen(['PotreeConverter', '--source', potree_ply, 
               '-a', 'RGB', 'INTENSITY', 'CLASSIFICATION', 
               '-o', potree_dirname, 'potree'])
  pid.wait()

