import os
from os import environ as env

from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task(base=VipTask, bind=True)
def create_height_map(self, voxel_world_id, render_height):
  import shutil
  import urllib

  import numpy as np

  import brl_init

  from boxm2_scene_adaptor import boxm2_scene_adaptor
  from boxm2_adaptor import ortho_geo_cam_from_scene, scene_lvcs, scene_bbox
  from vpgl_adaptor_boxm2_batch import convert_local_to_global_coordinates, geo2generic, save_geocam_to_tfw
  from vil_adaptor_boxm2_batch import save_image, scale_and_offset_values, stretch_image, image_range

  import vsi.io.image

  import voxel_globe.tools
  import voxel_globe.tools.hash
  import voxel_globe.tools.camera
  import voxel_globe.meta.models as models
  import voxel_globe.ingest.payload.tools

  with voxel_globe.tools.task_dir('height_map', cd=True) as processing_dir:
    voxel_world = models.VoxelWorld.objects.get(id=voxel_world_id)
    scene = boxm2_scene_adaptor(os.path.join(voxel_world.directory, 'scene.xml'), env['VIP_OPENCL_DEVICE'])
    ortho_camera, cols, rows = ortho_geo_cam_from_scene(scene.scene)
    tfw_camera = os.path.join(processing_dir, 'cam.tfw')
    save_geocam_to_tfw(ortho_camera, tfw_camera)
    with open(tfw_camera, 'r') as fid:
      geo_transform = [float(x) for x in fid.readlines()]

    (x0,y0,z0),(x1,y1,z1) = scene_bbox(scene.scene)
    lvcs = scene_lvcs(scene.scene)
    #lvcs = vpgl_adaptor.create_lvcs(lat=origin[1], lon=origin[0], el=origin[2],
    #                                csname="wgs84")
    _,_,min_height = convert_local_to_global_coordinates(lvcs, x0, y0, z0)
    if render_height is None:
      render_height = z1+(z1-z0)/1000
      #z1+(z1-z0)/1000 is basically to say "just a little above the top" *2 is
      #1) overkill and 2) doesn't work with sign, +1 could go crazy in an 
      #arbitrarily scaled system, so this just calculates ".1% more" which is
      #more than good enough
    else:
      render_height = render_height - voxel_world.origin[2]
    logger.critical("Render Height is %f (%s)", render_height, type(render_height))
    generic_camera = geo2generic(ortho_camera, cols, rows, render_height, 0)

    z_exp_img, z_var_img = scene.render_z_image(generic_camera, cols, rows)

    #This is TECHNICALLY wrong, it assumes the earth is flat. 
    scale_and_offset_values(z_exp_img, 1, min_height)
    
    height_filename = os.path.join(processing_dir, 'height.tif')
    
    save_image(z_exp_img, height_filename)

    checksum = voxel_globe.tools.hash.sha256_file(height_filename)
    
    with voxel_globe.tools.image_sha_dir(checksum) as image_dir:
      original_filename = os.path.join(image_dir, 'height_map.tif')
      
      #If the exact file exist already, don't ingest it again. Unlikely
      if not os.path.exists(original_filename):
        img = vsi.io.image.imread(height_filename)
        vsi.io.image.imwrite_geotiff(img.raster(), original_filename, 
                                     [geo_transform[x] for x in [4,0,1,5,2,3]])
  
        zoomify_filename = os.path.join(image_dir, 'zoomify.tif')
        img_min, img_max = image_range(z_exp_img)
        if img_min == img_max:
          zoomify_image = z_exp_img #At least it won't crash
        else:
          zoomify_image = stretch_image(z_exp_img, img_min, img_max, 'byte')

        save_image(zoomify_image, zoomify_filename)

        zoomify_name = os.path.join(image_dir, 'zoomify')
        voxel_globe.ingest.payload.tools.zoomify_image(zoomify_filename, zoomify_name)        
  
      img = voxel_globe.meta.models.Image(
            name="Height Map %s (%s)" % (voxel_world.name, 
                                         voxel_world.id), 
            image_width=cols, image_height=rows, 
            number_bands=1, pixel_format='f', file_format='zoom', 
            service_id=self.request.id)
      img.filename_path=original_filename
      img.save()

      image_set = models.ImageSet.objects.get_or_create(name="Height Maps", 
          defaults={"_attributes":'{"autogen":true}'})[0]
      image_set.images.add(img)

      gsd = scene.description['voxelLength']
      camera_center = ((x0+x1)/2, (y0+y1)/2, z1+10000)
      d = z1-z0+10000
      k=np.eye(3)
      k[0,2] = cols/2
      k[1,2] = rows/2
      k[0,0] = k[1,1] = d/gsd
      r=np.eye(3)
      r[0,0]=-1
      t = -r.T.dot(camera_center)

      camera=voxel_globe.tools.camera.save_krt(self.request.id, img, k, r, t,
                                               voxel_world.origin)
      camera_set=voxel_globe.meta.models.CameraSet(\
          name="Height Map %s (%s)" % (voxel_world.name, voxel_world.id), \
          images=image_set, service_id=self.request.id)
      camera_set.save()
      camera_set.cameras.add(camera)
  

@shared_task(base=VipTask, bind=True)
def height_map_error(self, image_id):
  
  import numpy as np

  import vpgl_adaptor_boxm2_batch as vpgl_adaptor
  
  from vsi.io.image import imread, GdalReader
  
  from voxel_globe.meta import models
  import voxel_globe.tools
  from voxel_globe.tools.celery import Popen

  from vsi.tools.file_util import lncp

  tie_points_yxz = []
  control_points_yxz = []

  image = models.Image.objects.get(id=image_id)

  height_reader =  GdalReader(image.filename_path, autoload=True)
  transform = height_reader.object.GetGeoTransform()
  height = height_reader.raster()
  del height_reader

  tie_points = image.tiepoint_set.all()

  for tie_point in tie_points:
    lla_xyz = tie_point.control_point.point.coords
    control_points_yxz.append([lla_xyz[x] for x in [1,0,2]])
    tie_points_yxz.append([transform[4]*(tie_point.point.coords[0]+0.5) + transform[5]*(tie_point.point.coords[1]+0.5) + transform[3],
                           transform[1]*(tie_point.point.coords[0]+0.5) + transform[2]*(tie_point.point.coords[1]+0.5) + transform[0],
                           height[tie_point.point.coords[1], tie_point.point.coords[0]]])

  origin_yxz = np.mean(np.array(control_points_yxz), axis=0)
  tie_points_local = []
  control_points_local = []
  lvcs = vpgl_adaptor.create_lvcs(origin_yxz[0], origin_yxz[1], origin_yxz[2], 'wgs84')

  for tie_point in tie_points_yxz:
    tie_points_local.append(vpgl_adaptor.convert_to_local_coordinates2(lvcs, *tie_point))

  for control_point in control_points_yxz:
    control_points_local.append(vpgl_adaptor.convert_to_local_coordinates2(lvcs, *control_point))

  error = np.linalg.norm(np.array(tie_points_local)-np.array(control_points_local), axis=0)/(len(tie_points_local)**0.5)

  result={}
  result['error'] = list(error)
  result['horizontal_accuracy'] = 2.4477*0.5*(error[0]+error[1])
  result['vertical_accuracy'] = 1.96*error[2]

  return result