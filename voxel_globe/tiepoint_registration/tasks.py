import os

from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task(base=VipTask, bind=True)
def tiepoint_registration(self, image_set_id):
  from PIL import Image
  import numpy as np

  from django.contrib.gis.geos import Point

  import vpgl_adaptor

  from vsi.io.krt import Krt

  from voxel_globe.meta import models
  import voxel_globe.tools
  from voxel_globe.tools.camera import get_krt, save_krt
  from voxel_globe.tools.celery import Popen

  from voxel_globe.tools.xml_dict import load_xml
  
  self.update_state(state='INITIALIZE', meta={'id':image_set_id})


  image_set = models.ImageSet.objects.get(id=image_set_id)

  control_points = {}

  for fr,image in enumerate(image_set.images.all()):
    tiepoints = image.tiepoint_set.all() 
    for tiepoint in tiepoints:
      #demoware code hack!
      if 'error' in tiepoint.control_point.name.lower():
        continue
      if tiepoint.control_point.id not in control_points:
        control_points[tiepoint.control_point.id] = {'tiepoints':{}}
      control_points[tiepoint.control_point.id]['tiepoints'][fr] = list(tiepoint.point)
      lla_xyz = tiepoint.control_point.point.coords
      control_points[tiepoint.control_point.id]['3d'] = [lla_xyz[x] for x in [1,0,2]]

  #filter only control points with more than 1 tiepoint
  control_points = {k:v for k,v in control_points.iteritems() if len(v['tiepoints'].keys()) > 1}

  origin_yxz = np.mean([v['3d'] for k,v in control_points.iteritems()], axis=0)
  lvcs = vpgl_adaptor.create_lvcs(origin_yxz[0], origin_yxz[1], origin_yxz[2], 'wgs84')
  for control_point in control_points:
    control_points[control_point]['lvcs'] = vpgl_adaptor.convert_to_local_coordinates2(lvcs, *control_points[control_point]['3d'])

  images = {}

  with voxel_globe.tools.task_dir('tiepoint_registration', cd=True) as processing_dir:
    dummy_imagename = os.path.join(processing_dir, 'blank.jpg')
    img = Image.fromarray(np.empty([1,1], dtype=np.uint8))
    img.save(dummy_imagename)
    #Thank you stupid site file
      
    for fr,image in enumerate(image_set.images.all()):
      (K,R,T,o) = get_krt(image)
      images[fr] = image.id

      with open(os.path.join(processing_dir, 'frame_%05d.txt' % fr), 'w') as fid:
        print >>fid, (("%0.18f "*3+"\n")*3) % (K[0,0], K[0,1], K[0,2], 
            K[1,0], K[1,1], K[1,2], K[2,0], K[2,1], K[2,2])
        print >>fid, (("%0.18f "*3+"\n")*3) % (R[0,0], R[0,1], R[0,2], 
            R[1,0], R[1,1], R[1,2], R[2,0], R[2,1], R[2,2])
        print >>fid, ("%0.18f "*3+"\n") % (T[0,0], T[1,0], T[2,0])
    site_in_name = os.path.join(processing_dir, 'site.xml')
    site_out_name = os.path.join(processing_dir, 'site2.xml')
    with open(site_in_name, 'w') as fid:
      fid.write('''<BWM_VIDEO_SITE name="Triangulation">
  <videoSiteDir path="%s">
  </videoSiteDir>
  <videoPath path="%s">
  </videoPath>
  <cameraPath path="%s/*.txt">
  </cameraPath>
  <Objects>
  </Objects>ve
  <Correspondences>\n''' % (processing_dir, dummy_imagename, processing_dir))
      for control_point_index, control_point_id in enumerate(control_points):
        fid.write('<Correspondence id="%d">\n' % control_point_index)
        for fr, tie_point in control_points[control_point_id]['tiepoints'].iteritems():
          fid.write('<CE fr="%d" u="%f" v="%f"/>\n' % (fr, tie_point[0], tie_point[1]))
        fid.write('</Correspondence>\n')
        control_points[control_point_id]['id'] = control_point_index
      fid.write('''</Correspondences>
  </BWM_VIDEO_SITE>\n''')
    
    #triangulate the points
    Popen(['bwm_triangulate_2d_corrs', '-site', site_in_name, '-out', site_out_name], logger=logger).wait()

    #Read in the result, and load into points_triangulate structure
    xml = load_xml(site_out_name)
    points_triangulate = {'id':[], 'x':[], 'y':[], 'z':[]}
    for correspondence in xml['Correspondences']['Correspondence']:
      points_triangulate['id'].append(int(correspondence.at['id']))
      points_triangulate['x'].append(float(correspondence['corr_world_point'].at['X']))
      points_triangulate['y'].append(float(correspondence['corr_world_point'].at['Y']))
      points_triangulate['z'].append(float(correspondence['corr_world_point'].at['Z']))
      
    #Read the points out of the control points structure, but make sure they are 
    #in the same order (check id == point_id
    points_orig = {'x':[], 'y':[], 'z':[]}
    for point_id in points_triangulate['id']:
      point = [v['lvcs'] for k,v in control_points.iteritems() if v['id'] == point_id]
      points_orig['x'].append(point[0][0])
      points_orig['y'].append(point[0][1])
      points_orig['z'].append(point[0][2])
    new_cameras = os.path.join(processing_dir, 'new_cameras')
    os.mkdir(new_cameras)
    
    #Make transformation
    transform, scale = vpgl_adaptor.compute_transformation(points_triangulate['x'], points_triangulate['y'], points_triangulate['z'],
                                        points_orig['x'],points_orig['y'],points_orig['z'],
                                        processing_dir, new_cameras)

    #calculate the new bounding box
    bbox_min, bbox_max = vpgl_adaptor.compute_transformed_box(list(image_set.scene.bbox_min), list(image_set.scene.bbox_max), transform)
    
    #calculate the new voxel size
    default_voxel_size=Point(*(x*scale for x in image_set.scene.default_voxel_size))
    
    scene = models.Scene(name=image_set.scene.name+' tiepoint registered', 
                         service_id=self.request.id,
                         origin=Point(origin_yxz[1], origin_yxz[0], origin_yxz[2]),
                         bbox_min=Point(*bbox_min),
                         bbox_max=Point(*bbox_max),
                         default_voxel_size=default_voxel_size,
                         geolocated=True)
    scene.save()
    image_set.scene=scene
    image_set.save()

    for fr, image_id in images.iteritems():
      krt = Krt.load(os.path.join(new_cameras, 'frame_%05d.txt' % fr))
      image = models.Image.objects.get(id=image_id)
      save_krt(self.request.id, image, krt.k, krt.r, krt.t, [origin_yxz[x] for x in [1,0,2]], srid=4326)


@shared_task(base=VipTask, bind=True)
def tiepoint_error_calculation(self, image_set_id, scene_id):
  from PIL import Image
  import numpy as np

  import vpgl_adaptor

  from voxel_globe.meta import models
  import voxel_globe.tools
  from voxel_globe.tools.camera import get_krt
  from voxel_globe.tools.celery import Popen

  from voxel_globe.tools.xml_dict import load_xml, XmlListConfig, XmlList

  self.update_state(state='INITIALIZE', meta={'id':image_set_id, 'scene':scene_id})

  image_set = models.ImageSet.objects.get(id=image_set_id)

  control_points = {}

  for fr,image in enumerate(image_set.images.all()):
    tiepoints = image.tiepoint_set.all() 
    for tiepoint in tiepoints:
      #demoware code hack!
      if tiepoint.control_point.id not in control_points:
        control_points[tiepoint.control_point.id] = {'tiepoints':{}}
      control_points[tiepoint.control_point.id]['tiepoints'][fr] = list(tiepoint.point)
      lla_xyz = tiepoint.control_point.point.coords
      control_points[tiepoint.control_point.id]['3d'] = [lla_xyz[x] for x in [1,0,2]]

  #filter only control points with more than 1 tiepoint
  control_points = {k:v for k,v in control_points.iteritems() if len(v['tiepoints'].keys()) > 1}

  origin_xyz = list(models.Scene.objects.get(id=scene_id).origin)
  lvcs = vpgl_adaptor.create_lvcs(origin_xyz[1], origin_xyz[0], origin_xyz[2], 'wgs84')
  for control_point in control_points:
    control_points[control_point]['lvcs'] = vpgl_adaptor.convert_to_local_coordinates2(lvcs, *control_points[control_point]['3d'])

  with voxel_globe.tools.task_dir('tiepoint_error_calculation', cd=True) as processing_dir:
    dummy_imagename = os.path.join(processing_dir, 'blank.jpg')
    img = Image.fromarray(np.empty([1,1], dtype=np.uint8))
    img.save(dummy_imagename)
    #Thank you stupid site file
      
    for fr,image in enumerate(image_set.images.all()):
      (K,R,T,o) = get_krt(image)

      with open(os.path.join(processing_dir, 'frame_%05d.txt' % fr), 'w') as fid:
        print >>fid, (("%0.18f "*3+"\n")*3) % (K[0,0], K[0,1], K[0,2], 
            K[1,0], K[1,1], K[1,2], K[2,0], K[2,1], K[2,2])
        print >>fid, (("%0.18f "*3+"\n")*3) % (R[0,0], R[0,1], R[0,2], 
            R[1,0], R[1,1], R[1,2], R[2,0], R[2,1], R[2,2])
        print >>fid, ("%0.18f "*3+"\n") % (T[0,0], T[1,0], T[2,0])
    site_in_name = os.path.join(processing_dir, 'site.xml')
    site_out_name = os.path.join(processing_dir, 'site2.xml')
    with open(site_in_name, 'w') as fid:
      fid.write('''<BWM_VIDEO_SITE name="Triangulation">
<videoSiteDir path="%s">
</videoSiteDir>
<videoPath path="%s">
</videoPath>
<cameraPath path="%s/*.txt">
</cameraPath>
<Objects>
</Objects>
<Correspondences>\n''' % (processing_dir, dummy_imagename, processing_dir))
      for control_point_index, control_point_id in enumerate(control_points):
        fid.write('<Correspondence id="%d">\n' % control_point_index)
        for fr, tie_point in control_points[control_point_id]['tiepoints'].iteritems():
          fid.write('<CE fr="%d" u="%f" v="%f"/>\n' % (fr, tie_point[0], tie_point[1]))
        fid.write('</Correspondence>\n')
        control_points[control_point_id]['id'] = control_point_index
      fid.write('''</Correspondences>
</BWM_VIDEO_SITE>\n''')
    
    #triangulate the points
    Popen(['bwm_triangulate_2d_corrs', '-site', site_in_name, '-out', site_out_name], logger=logger).wait()

    #Read in the result, and load into points_triangulate structure
    xml = load_xml(site_out_name)
    points_triangulate_id=[]
    points_triangulate=[]
    correspondences = xml['Correspondences']['Correspondence']
    if not isinstance(correspondences, XmlListConfig) and not isinstance(correspondences, XmlList):
      correspondences = [correspondences]
    for correspondence in correspondences:
      points_triangulate_id.append(int(correspondence.at['id']))
      points_triangulate.append((float(correspondence['corr_world_point'].at['X']),
                                 float(correspondence['corr_world_point'].at['Y']),
                                 float(correspondence['corr_world_point'].at['Z'])))
      
    #Read the points out of the control points structure, but make sure they are 
    #in the same order (check id == point_id
    points_orig = []
    for point_id in points_triangulate_id:
      point = [v['lvcs'] for k,v in control_points.iteritems() if v['id'] == point_id]
      points_orig.append(point[0])  

  points_orig = np.array(points_orig)
  points_triangulate = np.array(points_triangulate)
  error = np.linalg.norm((points_orig-points_triangulate), axis=0)/(points_orig.shape[0]**0.5)

  result={}
  result['error'] = list(error)
  result['horizontal_accuracy'] = 2.4477*0.5*(error[0]+error[1])
  result['vertical_accuracy'] = 1.96*error[2]

  return result