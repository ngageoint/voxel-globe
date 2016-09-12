from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task(base=VipTask, bind=True)
def runVisualSfm(self, imageSetId, sceneId, cleanup=True):
  from voxel_globe.meta import models

  from os import environ as env
  from os.path import join as path_join
  import os
  import shutil

  from django.contrib.gis.geos import Point
  
  from .tools import writeNvm, writeGcpFile, generateMatchPoints, runSparse,\
                     readNvm
  
  import voxel_globe.tools
  from voxel_globe.tools.wget import download as wget
  from voxel_globe.tools.camera import get_kto, save_krt
  import voxel_globe.tools.enu as enu
  import numpy

  import boxm2_adaptor
  import boxm2_scene_adaptor
  from voxel_globe.tools.xml_dict import load_xml
  
  from django.contrib.gis.geos import Point
  from voxel_globe.tools.image import convert_image

  from distutils.spawn import find_executable

  from glob import glob

  from vsi.tools.file_util import lncp
  
  self.update_state(state='INITIALIZE', meta={'stage':0})

  #Make main temp dir and cd into it
  with voxel_globe.tools.task_dir('visualsfm', cd=True) as processing_dir:

    #Because visualsfm is so... bad, I have to copy it locally so I can
    #configure it
    visualsfm_exe = os.path.join(processing_dir, 
        os.path.basename(os.environ['VIP_VISUALSFM_EXE']))
    shutil.copy(find_executable(os.environ['VIP_VISUALSFM_EXE']), 
                visualsfm_exe)
    with open(os.path.join(processing_dir, 'nv.ini'), 'w') as fid:
      fid.write('param_search_multiple_models 0\n')
      fid.write('param_use_siftgpu 2\n')

    matchFilename = path_join(processing_dir, 'match.nvm')
    sparce_filename = path_join(processing_dir, 'sparse.nvm')
    #This can NOT be changed in version 0.5.25  
    gcpFilename = matchFilename + '.gcp'
    logger.debug('Task %s is processing in %s' % (self.request.id, 
                                                  processing_dir))

    image_set = models.ImageSet.objects.get(
        id=imageSetId)
    imageList = image_set.images.all()

###    if 1:
###    try: #Not fully integrated yet
###      sift_gpu = siftgpu.SiftGPU()
###    except:
###      pass

    localImageList = []
    for x in range(len(imageList)):
      #Download the image locally
      image = imageList[x]
      self.update_state(state='INITIALIZE', meta={'stage':'image fetch', 'i':x,
                                                  'total':len(imageList)})
      imageName = image.filename_path
      extension = os.path.splitext(imageName)[1].lower()
      localName = path_join(processing_dir, 'frame_%05d%s' % (x+1, extension))
      lncp(imageName, localName)
  
      #Convert the image if necessary    
      if extension not in ['.jpg', '.jpeg', '.pgm', '.ppm']:
        self.update_state(state='INITIALIZE', 
            meta={'stage':'image convert', 'i':x, 'total':len(imageList)})
        #Add code here to converty to jpg for visual sfm
        if extension in ['.png']:#'not implemented':
          from PIL import Image
          image_temp = Image.open(localName)
          if len(image_temp.mode) > 1: #Stupid visual sfm is picky :(
            new_local_name = os.path.splitext(localName)[0] + '.ppm'
          else:
            new_local_name = os.path.splitext(localName)[0] + '.pgm'

          new_local_name = os.path.splitext(localName)[0] + '.jpg'

          ###ingest.convert_image(localName, new_local_name, 'PNM')
          convert_image(localName, new_local_name, 'JPEG', 
                        options=('QUALITY=100',))
          os.remove(localName)

          localName = new_local_name

        else:
          raise Exception('Unsupported file type')
        
      imageInfo = {'localName':localName, 'index':x}
  
      try:
        [K, T, llh] = get_kto(image)
        imageInfo['K_intrinsics'] = K
        imageInfo['transformation'] = T
        imageInfo['enu_origin'] = llh
      except:
        pass
  
      localImageList.append(imageInfo)
###      if 1:
###      try: #not fully integrated yet
###        sift_gpu.create_sift(localName, os.path.splitext(localName)[0]+'.sift')
###      except:
###        pass

  #  filenames = list(imageList.values_list('image_url'))
  #  logger.info('The image list 0is %s' % filenames)

    self.update_state(state='PROCESSING', 
                      meta={'stage':'generate match points', 
                            'processing_dir':processing_dir,
                            'total':len(imageList)})
    generateMatchPoints(map(lambda x:x['localName'], localImageList),
                        matchFilename, logger=logger, executable=visualsfm_exe)

  #   cameras = []
  #   for image in imageList:
  #     if 1:
  #     #try:
  #       [K, T, llh] = get_kto(image)
  #       cameras.append({'image':image.id, 'K':K, 'tranformation':
  #                       T, 'origin':llh})
  #     #except:
  #       pass  
  
  #  origin = numpy.median(origin, axis=0)
  #  origin = [-92.215197, 37.648858, 268.599]
    scene = models.Scene.objects.get(id=sceneId)
    origin = list(scene.origin)

    if scene.geolocated:
      self.update_state(state='PROCESSING', 
                        meta={'stage':'writing gcp points'})

      #find the middle origin, and make it THE origin
      data = []#.name .llh_xyz
      for imageInfo in localImageList:
        try:
          r = imageInfo['transformation'][0:3, 0:3]
          t = imageInfo['transformation'][0:3, 3:]
          enu_point = -r.transpose().dot(t)
    
          if not numpy.array_equal(imageInfo['enu_origin'], origin):
            ecef = enu.enu2xyz(refLong=imageInfo['enu_origin'][0],
                               refLat=imageInfo['enu_origin'][1],
                               refH=imageInfo['enu_origin'][2],
                               #e=imageInfo['transformation'][0, 3],
                               #n=imageInfo['transformation'][1, 3],
                               #u=imageInfo['transformation'][2, 3])
                               e=enu_point[0],
                               n=enu_point[1],
                               u=enu_point[2])
            enu_point = enu.xyz2enu(refLong=origin[0], 
                                    refLat=origin[1], 
                                    refH=origin[2],
                                    X=ecef[0],
                                    Y=ecef[1],
                                    Z=ecef[2])
    #      else:
    #        enu_point = imageInfo['transformation'][0:3, 3]
          
          dataBit = {'filename':imageInfo['localName'], 'xyz':enu_point}
          data.append(dataBit)
          
          #Make this a separate ingest process, making CAMERAS linked to the 
          #images
          #data = arducopter.loadAdjTaggedMetadata(
          #    r'd:\visualsfm\2014-03-20 13-22-44_adj_tagged_images.txt')
          #Make this read the cameras from the DB instead
          writeGcpFile(data, gcpFilename)

        except: #some images may have no camera 
          pass
    
    self.update_state(state='PROCESSING', meta={'stage':'sparse SFM'})
    runSparse(matchFilename, sparce_filename, gcp=scene.geolocated, 
              shared=True, logger=logger, executable=visualsfm_exe)
  
    self.update_state(state='FINALIZE', 
                      meta={'stage':'loading resulting cameras'})

    #prevent bundle2scene from getting confused and crashing
    sift_data = os.path.join(processing_dir, 'sift_data')
    os.mkdir(sift_data)
    for filename in glob(os.path.join(processing_dir, '*.mat')) +\
                    glob(os.path.join(processing_dir, '*.sift')):
      shutil.move(filename, sift_data)

    if scene.geolocated:
      #Create a uscene.xml for the geolocated case. All I want out of this is
      #the bounding box and gsd calculation.
      boxm2_adaptor.bundle2scene(sparce_filename, processing_dir, isalign=False,
                                 out_dir="")

      cams = readNvm(path_join(processing_dir, 'sparse.nvm'))
      #cams.sort(key=lambda x:x.name)
      #Since the file names are frame_00001, etc... and you KNOW this order is
      #identical to localImageList, with some missing

      camera_set = models.CameraSet(name="Visual SFM Geo %s" % image_set.name,
                                    service_id = self.request.id,
                                    images_id = imageSetId)
      camera_set.save()

      for cam in cams:
        frameName = cam.name #frame_00001, etc....
        imageInfo = filter(lambda x: x['localName'].endswith(frameName),
                           localImageList)[0]
        #I have to use endswith instead of == because visual sfm APPARENTLY 
        #decides to take some liberty and make absolute paths relative
        image = imageList[imageInfo['index']]

        (k,r,t) = cam.krt(width=image.image_width, height=image.image_height)
        t = t.flatten()
        camera = save_krt(self.request.id, image, k, r, t, origin, srid=4326)
        camera_set.cameras.add(camera)
    else:
      from vsi.tools.natural_sort import natural_sorted 
      from glob import glob
      
      from vsi.io.krt import Krt
      
      boxm2_adaptor.bundle2scene(sparce_filename, processing_dir, isalign=True,
                                 out_dir=processing_dir)
      #While the output dir is used for the b2s folders, uscene.xml is cwd
      #They are both set to processing_dir, so everything works out well
      aligned_cams = glob(os.path.join(processing_dir, 'cams_krt', '*'))
      #sort them naturally in case there are more then 99,999 files
      aligned_cams = natural_sorted(aligned_cams) 
      if len(aligned_cams) != len(imageList):
        #Create a new image set
        new_image_set = models.ImageSet(
            name="SFM Result Subset (%s)" % image_set.name, 
            service_id = self.request.id)
#        for image in image_set.images.all():
#          new_image_set.images.add(image)
        new_image_set.save()

        frames_keep = set(map(lambda x:
            int(os.path.splitext(x.split('_')[-2])[0])-1, aligned_cams))

        for frame_index in frames_keep:
          new_image_set.images.add(imageList[frame_index])

#        frames_remove = set(xrange(len(imageList))) - frames_keep 
#
#        for remove_index in list(frames_remove):
#          #The frame number refers to the nth image in the image set,
#          #so frame_00100.tif is the 100th image, starting the index at one
#          #See local_name above
#          
#          #remove the images sfm threw away 
#          new_image_set.remove(imageList[remove_index])
        image_set = new_image_set
        frames_keep = list(frames_keep)
      else:
        frames_keep = xrange(len(aligned_cams))

      camera_set = models.CameraSet(name="Visual SFM %s" % image_set.name,
                                    service_id = self.request.id,
                                    images_id = imageSetId)
      camera_set.save()

      #---Update the camera models in the database.---
      for camera_index, frame_index in enumerate(frames_keep):
        krt = Krt.load(aligned_cams[camera_index])
        image = imageList[frame_index]
        camera = save_krt(self.request.id, image, krt.k, krt.r, krt.t, [0,0,0], 
                          srid=4326)
        camera_set.cameras.add(camera)

      #---Update scene information important for the no-metadata case ---

    scene_filename = os.path.join(processing_dir, 'model', 'uscene.xml')
    boxm_scene = boxm2_scene_adaptor.boxm2_scene_adaptor(scene_filename)

    scene.bbox_min = Point(*boxm_scene.bbox[0])
    scene.bbox_max = Point(*boxm_scene.bbox[1])

    #This is not a complete or good function really... but it will get me the
    #information I need.
    scene_dict = load_xml(scene_filename)
    block = scene_dict['block']

    scene.default_voxel_size=Point(float(block.at['dim_x']),
                                   float(block.at['dim_y']),
                                   float(block.at['dim_z']))
    scene.save()
