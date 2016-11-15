from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

import os

@shared_task(base=VipTask, bind=True, routing_key="gpu")
def run_build_voxel_model(self, image_set_id, camera_set_id, scene_id, bbox, 
                          skip_frames, cleanup=True):

  import random

  from vsi.tools.redirect import StdRedirect
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
        copytree(processing_dir, voxel_world_dir, ignore=lambda x,y:['local'])
        models.VoxelWorld(
            name='%s world (%s)' % (imageSet.name, self.request.id),
            origin=scene.origin,
            directory=voxel_world_dir,
            service_id=self.request.id).save()

    return {"image_set_name" : imageSet.name}


@shared_task(base=VipTask, bind=True, routing_key="gpu")
def run_build_voxel_model_bp(self, image_set_id, camera_set_id, scene_id, bbox, 
                             skip_frames, cleanup=True):
  import random
  import glob
  import math

  import numpy as np

  from vsi.tools.redirect import StdRedirect
  from voxel_globe.meta import models
  from voxel_globe.tools.camera import get_krt
  import voxel_globe.tools

  from boxm2_scene_adaptor import boxm2_scene_adaptor

  import brl_init
  from vil_adaptor_boxm2_batch import load_image
  import vpgl_adaptor_boxm2_batch as vpgl

  from vsi.vxl.create_scene_xml import create_scene_xml

  from vsi.tools.dir_util import copytree
  from vsi.tools.file_util import lncp

  def rectint(recta,rectb):
    lx = max(recta[0],rectb[0])
    rx = min(recta[2],rectb[2])
    by = max(recta[1],rectb[1])
    ty = min(recta[3],rectb[3])

    if lx > rx or by > ty :
      return [0,0,0,0],0
    else:
      return [lx,by,rx,ty], (rx-lx)*(ty-by)

  def generate_subsetim(scene,camfiles,ni,nj):
    subsetIdx = []
    refIndices = []
    minDepOverlap = 0.25
    minRefOverlap = 0.5
    minIndepAngle = 5.0
    minRefAngle = 5.0
    maxRefAngle = 15.0
    minRefIndepAngle = 5.0
    cosMinIndepAngle = math.cos( minIndepAngle*math.pi/180.0 );
    cosMinRefAngle = math.cos( minRefAngle*math.pi/180.0 );
    cosMaxRefAngle = math.cos( maxRefAngle*math.pi/180.0 );
    cosMinRefIndepAngle = math.cos( minRefIndepAngle*math.pi/180.0 );
    bbox =  scene.bbox
    grect=[scene.bbox[0][0],scene.bbox[0][1],scene.bbox[1][0],scene.bbox[1][1]]
    worldoverlaps = []
    camrects = []
    cams = []
    princAxis = [] 
    for camfile in camfiles:
      pcam = vpgl.load_perspective_camera(camfile)
      prx,pry,prz=vpgl.get_backprojected_ray(pcam,ni/2,nj/2)
      princAxis.append([prx,pry,prz])
      Hmat = vpgl.compute_camera_to_world_homography(pcam,[0,0,1,-bbox[0][2]])
      H = np.array(Hmat).reshape([3,3])
      ps =  np.dot(H,np.transpose([[0,0,1],
                     [ni,0,1],
                     [ni,nj,1],
                     [0,nj,1]]))
      xs =  ps[0,:]/ps[2,:]
      ys =  ps[1,:]/ps[2,:]
      rect = [min(xs),min(ys),max(xs),max(ys)]
      area = (rect[2]-rect[0])*(rect[3]-rect[1])
      crect,carea = rectint(rect,grect)
      #print crect,carea
      if ( carea > 0 ):
        cams.append(pcam)
        camrects.append(crect)
        worldoverlaps.append(carea/area)

    usedcams = [False]*len(cams)
    for i in range(0,len(cams)):
      randidx = random.randint(0,len(cams)-1)
      while usedcams[randidx]:
        randidx = (randidx+1)%len(cams)
      usedcams[randidx]= True
      dep = False
      for c2 in range(0,len(subsetIdx)):
        cosAngle = np.dot(princAxis[randidx], princAxis[subsetIdx[c2]] )
        if  cosAngle > cosMinIndepAngle :
          rectc2 = camrects[subsetIdx[c2]]
          overlap,oarea = rectint(camrects[randidx] , rectc2)
          tarea = (rectc2[2]-rectc2[0])*(rectc2[3]-rectc2[1])
          if( oarea/tarea > minDepOverlap ):
            dep = True
            break
      if dep:
        continue
      theseRefIndices= []
      for c3 in range(0,len(cams)):
        #Check angle disparity
        cosAngle2 = np.dot(princAxis[randidx],princAxis[c3] );
        if( cosAngle2 > cosMinRefAngle or cosAngle2 < cosMaxRefAngle ):
          continue
        # Check that a similar viewpoint isn't already used for reference
        refDep = False
        for c4 in range(0,len(theseRefIndices)):
          #Check angle disparity
          cosAngle3 = np.dot(princAxis[theseRefIndices[c4]],princAxis[c3] );
          if( cosAngle3 > cosMinRefIndepAngle ):
            refDep = True
            break
          #If similar viewpoint don't add
        if( refDep ):
          continue
        theseRefIndices.append(c3)
            #If at least one reference image save this viewpoint
      if len(theseRefIndices) > 0 :
        subsetIdx.append( randidx );
        refIndices.append( theseRefIndices );
    return subsetIdx, refIndices

  def update_bp(scene, images, cameras, do_update_image=True, do_update_hmap=False):
    _, ni, nj = load_image (images[0])
    frames,refimages = generate_subsetim(scene,cameras,ni,nj)
    for file_name in glob.glob(os.path.join(scene.model_dir, 'boxm2_*.bin')):
      os.remove(file_name)
    scene.init_uniform_prob()
    
    sradius = 16
    idents = []
    weights = []
    if do_update_image:
      idents.append("if")
      weights.append(1.0)
    if do_update_hmap:
      idents.append("hf")
      weights.append(2.0)

    for idx, i in enumerate(frames):
      if do_update_image:
        print "Iteration ",idx,  "Image " , images[i];
        ####load image and camera
        viewid = os.path.splitext(os.path.basename(images[i]))[0]
        #### forming an app model using the neighbor images
        for lindex in refimages[idx]:
          lcam        = vpgl.load_perspective_camera(cameras[lindex]); 
          limg, ni, nj = load_image (images[lindex]);
          scene.update(lcam, limg,False, True,None ,"gpu0",0.05,viewid)

        scene.update_if(False,viewid)       # subtracting the image factor 
        scene.fuse_factors(idents,weights)  
        pcam        = vpgl.load_perspective_camera(cameras[i]); 
        img, ni, nj = load_image (images[i]);
        scene.compute_pre_post(pcam, img,viewid,100000,100000); # computing the new image factor 
        scene.update_if(True,viewid)       # adding the image factor 
        scene.fuse_factors(idents,weights)

      if do_update_hmap and idx % 2 == 0:     
        scene.update_hf(False)              # subtracting the height-map factor 
        scene.fuse_factors(idents,weights)
        zimg,zvar,ximg,yimg,probimg = scene.render_height_map()
        #save_image(zimg, "./zimg.tif")
        scene.compute_hmapf(zimg,zvar,ximg,yimg,sradius) # computing the height-map factor
        scene.update_hf(True)                            # adding the height-map factor
        scene.fuse_factors(idents,weights)

    scene.write_cache()

  def refine(scene):
    scene.refine(0.3)
    for filename in glob.glob(os.path.join(scene.model_dir, '[a-b]*.bin')):
      os.remove(filename)
    scene.write_cache()

  with StdRedirect(open(os.path.join(voxel_globe.tools.log_dir(), 
                                     self.request.id)+'_out.log', 'w'),
                   open(os.path.join(voxel_globe.tools.log_dir(), 
                                     self.request.id)+'_err.log', 'w')):

    openclDevice = os.environ['VIP_OPENCL_DEVICE']
    opencl_memory = os.environ.get('VIP_OPENCL_MEMORY', None)
    if opencl_memory:
      opencl_memory = int(opencl_memory)

    scene = models.Scene.objects.get(id=scene_id)
    imageSet = models.ImageSet.objects.get(id=image_set_id)
    imageList = imageSet.images.all()

    with voxel_globe.tools.task_dir('voxel_world') as processing_dir:
      logger.warning(bbox)

      create_scene_xml(openclDevice, 0, float(bbox['voxel_size']), 
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
      self.update_state(state='INITIALIZE', meta={'image_set_name': imageSet.name,
                                                  'stage':'camera fetch'})
      for image in imageList:
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
      # loaded_imgs = []
      # loaded_cams = []
    
      # for i in range(0, len(imageNames), skip_frames):
      #   logger.debug("i: %d img name: %s cam name: %s", i, imageNames[i], 
      #                cameraNames[i])
      #   self.update_state(state='PRELOADING', meta={'image_set_name': imageSet.name,
      #                                               'stage':'image load', 
      #                                               'i':i, 
      #                                               'total':len(imageNames)})
      #   img, ni, nj = load_image(imageNames[i])
      #   loaded_imgs.append(img)
      #   pcam = load_perspective_camera(cameraNames[i])
      #   loaded_cams.append(pcam)
    
      refine_cnt = 2

      for rfk in range(0, refine_cnt, 1):

        self.update_state(state='PROCESSING', meta={'image_set_name': imageSet.name,
            'stage':'update 1'})
        update_bp(vxl_scene, imageNames, cameraNames)
      # self.update_state(state='PROCESSING', meta={'image_set_name': imageSet.name,
      #     'stage':'update 2'})
      # update_bp(vxl_scene, imageNames, cameraNames, True, True)
      # self.update_state(state='PROCESSING', meta={'image_set_name': imageSet.name,
      #     'stage':'update 3'})
      # update_bp(vxl_scene, imageNames, cameraNames, True, True)

        if rfk < refine_cnt-1:
          self.update_state(state='PROCESSING', 
                            meta={'image_set_name': imageSet.name,
                                  'stage':'refine', 'i':rfk+1, 
                                  'total':refine_cnt})
          refine(vxl_scene)

      #Update color appearance

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

      for idx, (image_name, camera_name) in enumerate(zip(imageNames, cameraNames)):
        self.update_state(state='PROCESSING', meta={
            'image_set_name': imageSet.name,
            'stage':'color_update', 
            'i':idx+1, 'total':len(imageNames),
            'images':len(imageNames)})
        img, _, _ = load_image(image_name)
        pcam = vpgl.load_perspective_camera(camera_name)
        logger.debug("color_paint idx: %d", idx)
        vxl_scene.update(pcam,img,False,False,None,openclDevice,
                         tnear = 1000.0, tfar = 100000.0)

      vxl_scene.write_cache()

      with voxel_globe.tools.storage_dir('voxel_world') as voxel_world_dir:
        copytree(processing_dir, voxel_world_dir, ignore=lambda x,y:['local'])
        models.VoxelWorld(
            name='%s world (%s)' % (imageSet.name, self.request.id),
            origin=scene.origin,
            directory=voxel_world_dir,
            service_id=self.request.id).save()

    return {"image_set_name" : imageSet.name}
