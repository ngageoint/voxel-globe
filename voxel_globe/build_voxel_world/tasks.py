from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

import os

@shared_task(base=VipTask, bind=True)
def run_build_voxel_model(self, image_set_id, camera_set_id, scene_id, bbox, 
                          skip_frames, cleanup=True):

  from distutils.dir_util import remove_tree
  from shutil import move
  import random

  from vsi.tools.redirect import StdRedirect, Logger as LoggerWrapper
  from voxel_globe.meta import models
  from voxel_globe.tools.camera import get_krt
  import voxel_globe.tools

  from boxm2_scene_adaptor import boxm2_scene_adaptor

  import brl_init
  from vil_adaptor_boxm2_batch import load_image
  from vpgl_adaptor_boxm2_batch import load_perspective_camera

  from vsi.vxl.create_scene_xml import create_scene_xml

  from vsi.tools.dir_util import copytree
  from vsi.tools.file_util import lncp

  with StdRedirect(open(os.path.join(voxel_globe.tools.log_dir(), 
                                     self.request.id)+'_out.log', 'w'),
                   open(os.path.join(voxel_globe.tools.log_dir(), 
                                     self.request.id)+'_err.log', 'w')):

    openclDevice = os.environ['VIP_OPENCL_DEVICE']
    opencl_memory = os.environ.get('VIP_OPENCL_MEMORY', None)
    if opencl_memory:
      opencl_memory = int(opencl_memory)

    scene = models.Scene.objects.get(id=scene_id)

    imageSet = models.ImageSet.objects.get(\
        id=image_set_id)
    imageList = imageSet.images.all()

    with voxel_globe.tools.task_dir('voxel_world') as processing_dir:

      logger.warning(bbox)

      create_scene_xml(openclDevice, 3, float(bbox['voxel_size']), 
          lvcs1=(float(bbox['x_min']), float(bbox['y_min']), 
                 float(bbox['z_min'])), 
          lvcs2=(float(bbox['x_max']), float(bbox['y_max']), 
                 float(bbox['z_max'])),
          origin=scene.origin, model_dir='.', number_bins=1,
          output_file=open(os.path.join(processing_dir, 'scene.xml'), 'w'),
          n_bytes_gpu=opencl_memory)

      counter = 1

      imageNames = []
      cameraNames = []

      os.mkdir(os.path.join(processing_dir, 'local'))
      
      #Prepping
      for image in imageList:
        self.update_state(state='INITIALIZE', meta={'image_set_name': imageSet.name,
                                                    'stage':'image fetch', 
                                                    'i':counter, 
                                                    'total':len(imageList)})
        (K,R,T,o) = get_krt(image, camera_set_id)
        
        krtName = os.path.join(processing_dir, 'local', 'frame_%05d.krt' % counter)
        
        with open(krtName, 'w') as fid:
          print >>fid, (("%0.18f "*3+"\n")*3) % (K[0,0], K[0,1], K[0,2], 
              K[1,0], K[1,1], K[1,2], K[2,0], K[2,1], K[2,2])
          print >>fid, (("%0.18f "*3+"\n")*3) % (R[0,0], R[0,1], R[0,2], 
              R[1,0], R[1,1], R[1,2], R[2,0], R[2,1], R[2,2])
    
          print >>fid, ("%0.18f "*3+"\n") % (T[0,0], T[1,0], T[2,0])
        
        imageName = image.filename_path
        extension = os.path.splitext(imageName)[1]
        localName = os.path.join(processing_dir, 'local', 
                                 'frame_%05d%s' % (counter, extension))
        lncp(imageName, localName)
        
        counter += 1
      
        imageNames.append(localName)
        cameraNames.append(krtName)
        
      variance = 0.06
      
      vxl_scene = boxm2_scene_adaptor(os.path.join(processing_dir, "scene.xml"),
                                  openclDevice)
      current_level = 0
    
      loaded_imgs = []
      loaded_cams = []
    
      for i in range(0, len(imageNames), skip_frames):
        logger.debug("i: %d img name: %s cam name: %s", i, imageNames[i], 
                     cameraNames[i])
        self.update_state(state='PRELOADING', meta={'image_set_name': imageSet.name,
                                                    'stage':'image load', 
                                                    'i':i, 
                                                    'total':len(imageNames)})
        img, ni, nj = load_image(imageNames[i])
        loaded_imgs.append(img)
        pcam = load_perspective_camera(cameraNames[i])
        loaded_cams.append(pcam)
    
      refine_cnt = 5

      for rfk in range(0, refine_cnt, 1):
        pair = zip(loaded_imgs, loaded_cams)
        random.shuffle(pair)
        for idx, (img, cam) in enumerate(pair):
          self.update_state(state='PROCESSING', meta={'image_set_name': imageSet.name,
              'stage':'update', 
              'i':rfk+1, 'total':refine_cnt, 'image':idx+1, 
              'images':len(loaded_imgs)})
          logger.debug("refine_cnt: %d, idx: %d", rfk, idx)
          vxl_scene.update(cam,img,True,True,None,openclDevice,variance,
                       tnear = 1000.0, tfar = 100000.0)
    
        logger.debug("writing cache: %d", rfk)
        vxl_scene.write_cache()
        logger.debug("wrote cache: %d", rfk)
        
        if rfk < refine_cnt-1:
          self.update_state(state='PROCESSING', meta={'image_set_name': imageSet.name,
                                                      'stage':'refine', 
                                                      'i':rfk, 
                                                      'total':refine_cnt})
          logger.debug("refining %d...", rfk)
          vxl_scene.refine(0.3, openclDevice)
          vxl_scene.write_cache()


      with open(os.path.join(processing_dir, "scene_color.xml"), 'w') as fid:
        lines = open(os.path.join(processing_dir, "scene.xml"), 
                                  'r').readlines()
        lines = [line.replace('boxm2_mog3_grey', 
                              'boxm2_gauss_rgb').replace(
                              'boxm2_num_obs',
                              'boxm2_num_obs_single') for line in lines]
        fid.writelines(lines)

      vxl_scene = boxm2_scene_adaptor(os.path.join(processing_dir, 
                                                   "scene_color.xml"),
                                      openclDevice)

      for idx, (img, cam) in enumerate(pair):
        self.update_state(state='PROCESSING', meta={'image_set_name': imageSet.name,
                                                    'stage':'color_update', 
            'i':rfk+1, 'total':refine_cnt, 'image':idx+1, 
            'images':len(loaded_imgs)})
        logger.debug("color_paint idx: %d", idx)
        vxl_scene.update(cam,img,False,False,None,openclDevice,
                         tnear = 1000.0, tfar = 100000.0)

      vxl_scene.write_cache()

      with voxel_globe.tools.storage_dir('voxel_world') as voxel_world_dir:
        copytree(processing_dir, voxel_world_dir, ignore=lambda x,y:['images'])
        models.VoxelWorld(
            name='%s world (%s)' % (imageSet.name, self.request.id),
            origin=scene.origin,
            directory=voxel_world_dir,
            service_id=self.request.id).save()

    return {"image_set_name" : imageSet.name}


@shared_task(base=VipTask, bind=True)
def run_build_voxel_model_bp(self, image_set_id, camera_set_id, scene_id, bbox, 
                             skip_frames, cleanup=True):
  from distutils.dir_util import remove_tree
  from shutil import move
  import random

  from vsi.tools.redirect import StdRedirect, Logger as LoggerWrapper
  from voxel_globe.meta import models
  from voxel_globe.tools.camera import get_krt
  import voxel_globe.tools

  from boxm2_scene_adaptor import boxm2_scene_adaptor

  from vil_adaptor_boxm2_batch import load_image
  from vpgl_adaptor_boxm2_batch import load_perspective_camera

  from vsi.vxl.create_scene_xml import create_scene_xml

  from vsi.tools.dir_util import copytree

  with StdRedirect(open(os.path.join(voxel_globe.tools.log_dir(), 
                                     self.request.id)+'_out.log', 'w'),
                   open(os.path.join(voxel_globe.tools.log_dir(), 
                                     self.request.id)+'_err.log', 'w')):

    openclDevice = os.environ['VIP_OPENCL_DEVICE']
    opencl_memory = os.environ.get('VIP_OPENCL_MEMORY', None)
    if opencl_memory:
      opencl_memory = int(opencl_memory)

    scene = models.Scene.objects.get(id=scene_id)

    imageSet = models.ImageSet.objects.get(\
        id=image_set_id)
    imageList = imageSet.images.all()

    with voxel_globe.tools.task_dir('voxel_world') as processing_dir:

      logger.warning(bbox)

      if bbox['geolocated']:
        create_scene_xml(openclDevice, 3, float(bbox['voxel_size']), 
            lla1=(float(bbox['x_min']), float(bbox['y_min']), 
                  float(bbox['z_min'])), 
            lla2=(float(bbox['x_max']), float(bbox['y_max']), 
                  float(bbox['z_max'])),
            origin=scene.origin, model_dir='.', number_bins=1,
            output_file=open(os.path.join(processing_dir, 'scene.xml'), 'w'),
            n_bytes_gpu=opencl_memory)
      else:
        create_scene_xml(openclDevice, 3, float(bbox['voxel_size']), 
            lvcs1=(float(bbox['x_min']), float(bbox['y_min']), 
                   float(bbox['z_min'])), 
            lvcs2=(float(bbox['x_max']), float(bbox['y_max']), 
                   float(bbox['z_max'])),
            origin=scene.origin, model_dir='.', number_bins=1,
            output_file=open(os.path.join(processing_dir, 'scene.xml'), 'w'),
            n_bytes_gpu=opencl_memory)

      counter = 1
      
      imageNames = []
      cameraNames = []

      os.mkdir(os.path.join(processing_dir, 'local'))
      
      #Prepping
      for image in imageList:
        self.update_state(state='INITIALIZE', meta={'stage':'image fetch', 
                                                    'i':counter, 
                                                    'total':len(imageList)})
        (K,R,T,o) = get_krt(image, camera_set_id)

        krtName = os.path.join(processing_dir, 'local', 'frame_%05d.krt' % counter)

        with open(krtName, 'w') as fid:
          print >>fid, (("%0.18f "*3+"\n")*3) % (K[0,0], K[0,1], K[0,2], 
              K[1,0], K[1,1], K[1,2], K[2,0], K[2,1], K[2,2])
          print >>fid, (("%0.18f "*3+"\n")*3) % (R[0,0], R[0,1], R[0,2], 
              R[1,0], R[1,1], R[1,2], R[2,0], R[2,1], R[2,2])

          print >>fid, ("%0.18f "*3+"\n") % (T[0,0], T[1,0], T[2,0])

        imageName = image.filename_path
        extension = os.path.splitext(imageName)[1]
        localName = os.path.join(processing_dir, 'local', 
                                 'frame_%05d%s' % (counter, extension))
        lncp(imageName, localName)

        counter += 1

        imageNames.append(localName)
        cameraNames.append(krtName)

      variance = 0.06

      vxl_scene = boxm2_scene_adaptor(os.path.join(processing_dir, "scene.xml"),
                                  openclDevice)

      current_level = 0

      loaded_imgs = []
      loaded_cams = []

      for i in range(0, len(imageNames), skip_frames):
        logger.debug("i: %d img name: %s cam name: %s", i, imageNames[i], 
                     cameraNames[i])
        self.update_state(state='PRELOADING', meta={'stage':'image load', 
                                                    'i':i, 
                                                    'total':len(imageNames)})
        img, ni, nj = load_image(imageNames[i])
        loaded_imgs.append(img)
        pcam = load_perspective_camera(cameraNames[i])
        loaded_cams.append(pcam)
    
      refine_cnt = 5

      for rfk in range(0, refine_cnt, 1):
        pair = zip(loaded_imgs, loaded_cams)
        random.shuffle(pair)
        for idx, (img, cam) in enumerate(pair):
          self.update_state(state='PROCESSING', meta={'stage':'update', 
              'i':rfk+1, 'total':refine_cnt, 'image':idx+1, 
              'images':len(loaded_imgs)})
          logger.debug("refine_cnt: %d, idx: %d", rfk, idx)
          vxl_scene.update(cam,img,True,True,None,openclDevice,variance,
                       tnear = 1000.0, tfar = 100000.0)

        for bp_index in range(2):
          pass #height map update?

    
        logger.debug("writing cache: %d", rfk)
        vxl_scene.write_cache()
        logger.debug("wrote cache: %d", rfk)
        
        if rfk < refine_cnt-1:
          self.update_state(state='PROCESSING', meta={'stage':'refine', 
                                                      'i':rfk, 
                                                      'total':refine_cnt})
          logger.debug("refining %d...", rfk)
          vxl_scene.refine(0.3, openclDevice)
          vxl_scene.write_cache()


      with open(os.path.join(processing_dir, "scene_color.xml"), 'w') as fid:
        lines = open(os.path.join(processing_dir, "scene.xml"), 
                                  'r').readlines()
        lines = [line.replace('boxm2_mog3_grey', 
                              'boxm2_gauss_rgb').replace(
                              'boxm2_num_obs',
                              'boxm2_num_obs_single') for line in lines]
        fid.writelines(lines)

      vxl_scene = boxm2_scene_adaptor(os.path.join(processing_dir, 
                                                   "scene_color.xml"),
                                      openclDevice)

      for idx, (img, cam) in enumerate(pair):
        self.update_state(state='PROCESSING', meta={'stage':'color_update', 
            'i':rfk+1, 'total':refine_cnt, 'image':idx+1, 
            'images':len(loaded_imgs)})
        logger.debug("color_paint idx: %d", idx)
        vxl_scene.update(cam,img,False,False,None,openclDevice[0:3],
                         tnear = 1000.0, tfar = 100000.0)

      vxl_scene.write_cache()

      with voxel_globe.tools.storage_dir('voxel_world') as voxel_world_dir:
        copytree(processing_dir, voxel_world_dir, ignore=lambda x,y:['images'])
        models.VoxelWorld(
            name='%s world (%s)' % (imageSet.name, self.request.id),
            origin=scene.origin,
            directory=voxel_world_dir,
            service_id=self.request.id).save()

  return {
    'image_set_name': imageSet.name,
    'i': len(imageList),
    'total': len(imageList)
  }