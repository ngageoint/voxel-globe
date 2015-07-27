from ..common_tasks import app, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

import os

@app.task(base=VipTask, bind=True)
def run_build_voxel_model(self, image_collection_id, scene_id, bbox, 
                          skip_frames, cleanup=True, history=None):
  from vsi.tools.redirect import Redirect, Logger as LoggerWrapper
  from voxel_globe.meta import models
  from voxel_globe.tools.camera import get_krt
  import voxel_globe.tools

  from boxm2_scene_adaptor import boxm2_scene_adaptor

  from vil_adaptor import load_image
  from vpgl_adaptor import load_perspective_camera
  from voxel_globe.tools.wget import download as wget

  from vsi.vxl.create_scene_xml import create_scene_xml

  from distutils.dir_util import remove_tree
  from shutil import move
  from vsi.tools.dir_util import copytree, mkdtemp

  with Redirect(stdout_c=LoggerWrapper(logger, lvl=logging.INFO), 
                stderr_c=LoggerWrapper(logger, lvl=logging.WARNING)):  
    
    openclDevice = os.environ['VIP_OPENCL_DEVICE']
    
    scene = models.Scene.objects.get(id=scene_id)
    
    imageCollection = models.ImageCollection.objects.get(\
        id=image_collection_id).history(history);
    imageList = imageCollection.images.all();

    with voxel_globe.tools.taskDir() as processing_dir:

      logger.warning(bbox)

      if bbox['geolocated']:
        create_scene_xml(openclDevice, 3, float(bbox['voxel_size']), 
            lla1=(float(bbox['x_min']), float(bbox['y_min']), 
                  float(bbox['z_min'])), 
            lla2=(float(bbox['x_max']), float(bbox['y_max']), 
                  float(bbox['z_max'])),
            origin=scene.origin, model_dir='.', number_bins=1,
            output_file=open(os.path.join(processing_dir, 'scene.xml'), 'w'))
      else:
        create_scene_xml(openclDevice, 3, float(bbox['voxel_size']), 
            lvcs1=(float(bbox['x_min']), float(bbox['y_min']), 
                   float(bbox['z_min'])), 
            lvcs2=(float(bbox['x_max']), float(bbox['y_max']), 
                   float(bbox['z_max'])),
            origin=scene.origin, model_dir='.', number_bins=1,
            output_file=open(os.path.join(processing_dir, 'scene.xml'), 'w'))

      counter = 1;
      
      imageNames = []
      cameraNames = []

      os.mkdir(os.path.join(processing_dir, 'local'))
      
      #Prepping
      for image in imageList:
        self.update_state(state='INITIALIZE', meta={'stage':'image fetch', 
                                                    'i':counter, 
                                                    'total':len(imageList)})
        image = image.history(history)
        (K,R,T,o) = get_krt(image.history(history), history=history)
        
        krtName = os.path.join(processing_dir, 'local', 'frame_%05d.krt' % counter)
        
        with open(krtName, 'w') as fid:
          print >>fid, (("%0.18f "*3+"\n")*3) % (K[0,0], K[0,1], K[0,2], 
              K[1,0], K[1,1], K[1,2], K[2,0], K[2,1], K[2,2]);
          print >>fid, (("%0.18f "*3+"\n")*3) % (R[0,0], R[0,1], R[0,2], 
              R[1,0], R[1,1], R[1,2], R[2,0], R[2,1], R[2,2]);
    
          print >>fid, ("%0.18f "*3+"\n") % (T[0,0], T[1,0], T[2,0]);
        
        imageName = image.originalImageUrl;
        extension = os.path.splitext(imageName)[1]
        localName = os.path.join(processing_dir, 'local', 
                                 'frame_%05d%s' % (counter, extension));
        wget(imageName, localName, secret=True)
        
        counter += 1;
      
        imageNames.append(localName)
        cameraNames.append(krtName)
        
      variance = 0.06
      
      vxl_scene = boxm2_scene_adaptor(os.path.join(processing_dir, "scene.xml"),
                                  openclDevice);
    
      current_level = 0;
    
      loaded_imgs = [];
      loaded_cams = [];
    
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
    
      refine_cnt = 5;
      for rfk in range(0, refine_cnt, 1):
        for idx, (img, cam) in enumerate(zip(loaded_imgs, loaded_cams)):
          self.update_state(state='PROCESSING', meta={'stage':'update', 
              'i':rfk+1, 'total':refine_cnt, 'image':idx+1, 
              'images':len(loaded_imgs)})
          logger.debug("refine_cnt: %d, idx: %d", rfk, idx)
          vxl_scene.update(cam,img,True,True,None,openclDevice[0:3],variance,
                       tnear = 1000.0, tfar = 100000.0);
    
        logger.debug("writing cache: %d", rfk)
        vxl_scene.write_cache();
        logger.debug("wrote cache: %d", rfk)
        
        if rfk < refine_cnt-1:
          self.update_state(state='PROCESSING', meta={'stage':'refine', 
                                                      'i':rfk, 
                                                      'total':refine_cnt})
          logger.debug("refining %d...", rfk)
          refine_device = openclDevice[0:3]
          if refine_device == 'cpu':
            refine_device = 'cpp'
          vxl_scene.refine(0.3, refine_device);
          vxl_scene.write_cache();

      
      voxel_world_dir = mkdtemp(dir=os.environ['VIP_STORAGE_DIR'])
      copytree(processing_dir, voxel_world_dir, ignore=lambda x,y:['images'])
      models.VoxelWorld.create(name='%s world (%s)' % (imageCollection.name, 
                                                       self.request.id),
                               origin=scene.origin,
                               voxel_world_dir=voxel_world_dir,
                               service_id=self.request.id).save();

          
      ''' The rest of this is crap preview code '''
      logger.debug("Bandage-ing")
      from distutils.dir_util import mkpath
      ingestDir = mkdtemp(dir=os.environ['VIP_IMAGE_SERVER_ROOT']);
      os.chmod(ingestDir, 0775)
      expectedDir = os.path.join(ingestDir, 'preview')
      mkpath(expectedDir)
      logger.debug("Flying through...")
      render_fly_through(vxl_scene, expectedDir, 1024, 1024)
      logger.debug("Flew through...")
      
      from voxel_globe.no_metadata.tasks import ingest_data
      from voxel_globe.ingest.models import UploadSession
      import django.contrib.auth.models
      some_owner_id = django.contrib.auth.models.User.objects.all()[0].id 
      #sacrificial uploadSession
      uploadSession = UploadSession.objects.create(name='Voxel preview %s' % \
                                                   imageCollection.name, 
                                                   owner_id=some_owner_id)
      logger.debug("Starting upload...")
      ingest_data.apply(args=(uploadSession.id, ingestDir))
      logger.debug("Uploaded!")


def render_fly_through(scene, outDir, width, height):
  from boxm2_adaptor import init_trajectory,trajectory_next
  from boxm2_scene_adaptor import persp2gen, stretch_image, save_image
  from boxm2_register import remove_data
  logger.debug('render_fly_through(%s, %s, %s)', outDir, width, height)
  startInc = 45.0   #start incline angle off nadir
  endInc = 45.0     #end incline angle off nadir
  radius   = -1.0   #radius -1 defaults to half width of the volume

  trajectory = init_trajectory(scene.scene, startInc, endInc, radius, 
                               width, height)
  min_value = 0.0 
  max_value = 1.0
  
  increments = 10
  counter = 1
  for x in range(0, 500, 1):
    logger.debug('pre next %d', x)
    prcam = trajectory_next(trajectory)
    logger.debug('post next %d', x)
    if x % increments == 0:
      logger.debug('pre render %d', x)
      expimg = scene.render(prcam, width, height)
      logger.debug('pre stretch %d', x)
      expimg_s = stretch_image(expimg, min_value, max_value, 'byte')
      logger.debug('pre save %d', x)
      save_image(expimg_s, os.path.join(outDir, 'expected_%05d.tif'%counter))
      logger.debug('pre remove %d', x)
      remove_data(expimg.id)
      logger.debug('post remove %d', x)
      counter += 1
    remove_data(prcam.id)


