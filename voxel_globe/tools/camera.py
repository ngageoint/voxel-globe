from __future__ import absolute_import

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

import numpy
from django.contrib.gis.geos import Point

import voxel_globe.meta.models as models

def save_krt(service_id, image, k, r, t, origin, srid=4326, attributes={}):
  '''Saves the appropriate krt model to the image
  
     Keyword Arguments:
     service_id - Id field from the celery task calling this function
     image - voxel_globe.meta.Image object or object_id number
     k - 3x3 numpy.array
     r - 3x3 numpy.array
     t - 3 numpy.array
     origin - 3 numpy.arry, longitude, latitude, altitude in xyz order
     srid - srid number for origin

     Optional Arguments:
     attributes - Attributes dictionary
  '''

  if not hasattr(image, 'name'): #duck type, for maximum flexibility
    image =  models.Image.objects.get(id=image)

#  (k,r,t) = cam.krt(width=image.image_width, height=image.image_height)
#  logger.info('Origin is %s' % str(origin))

  grcs = models.GeoreferenceCoordinateSystem(
                  name='%s 0' % image.name,
                  x_unit='d', y_unit='d', z_unit='m',
                  location=Point(origin[0], origin[1], origin[2], srid=srid),
                  service_id = service_id)
  grcs.save()
  cs = models.CartesianCoordinateSystem(
                  name='%s 1' % (image.name),
                  service_id = service_id,
                  x_unit='m', y_unit='m', z_unit='m')
  cs.save()

  transform = models.CartesianTransform(
                       name='%s 1_0' % (image.name),
                       service_id = service_id,
                       rodriguezX=Point(*r[0,:]),
                       rodriguezY=Point(*r[1,:]),
                       rodriguezZ=Point(*r[2,:]),
                       translation=Point(t[0], t[1], t[2]),
                       coordinate_system_from_id=grcs.id,
                       coordinate_system_to_id=cs.id)
  transform.save()

  camera = models.Camera(name=image.name, service_id = service_id, image=image,
                         focal_length=Point(k[0,0], k[1,1]),
                         principal_point=Point(k[0,2], k[1,2]),
                         coordinate_system=cs, attributes=attributes)
  camera.save()
  return camera

def save_rpc(service_id, image, attributes={}):
  cs = models.CartesianCoordinateSystem(
                  name='%s' % (image.name),
                  service_id = service_id,
                  x_unit='m', y_unit='m', z_unit='m')
  cs.save()

  camera = models.Camera(name=image.name, service_id = service_id, image=image,
                         focal_length=Point(0, 0),
                         principal_point=Point(0, 0),
                         coordinate_system=cs, attributes=attributes)
  camera.save()
  return camera

def get_krt(image, camera_set_id=None, origin=None, eps=1e-9):
  ''' returns K, T, llh_origin (lon, lat, h)'''
  
  if camera_set_id:
    camera = image.camera_set.get(cameraset=camera_set_id)
  else:
    #TOTAL HACK Camera sets need to be fully plumbed. This prevents multiple cameras per image for now
    camera = image.camera_set.all()[0]

  K_i = numpy.eye(3)
  K_i[0,2] = camera.principal_point[0]
  K_i[1,2] = camera.principal_point[1]
  K_i[0,0] = camera.focal_length[0]
  K_i[1,1] = camera.focal_length[1]
  
  llh = [None]
  
  coordinate_systems = [camera.coordinate_system]
  coordinate_transforms = []
  while len(coordinate_systems[0].coordinatetransform_to_set.all()):
    #While the first coordinate system has a transform, pre-pend it to the list
    ct = coordinate_systems[0].coordinatetransform_to_set.all().select_subclasses()[0]

    #cs = ct.coordinate_system_from.get_subclasses()[0]
    cs = ct.coordinate_system_from.select_subclasses()[0]
    coordinate_transforms = [ct]+coordinate_transforms
    coordinate_systems = [cs] + coordinate_systems
  
  if isinstance(coordinate_systems[0], models.GeoreferenceCoordinateSystem):
    llh = list(coordinate_systems[0].location)
  
  T_camera_0 = numpy.eye(4)
  for ct in coordinate_transforms:
    T = numpy.eye(4)
    T[0,0:3] = ct.rodriguezX
    T[1,0:3] = ct.rodriguezY
    T[2,0:3] = ct.rodriguezZ
    T[0:3, 3] = ct.translation
    T_camera_0 = T.dot(T_camera_0)
    
    R = T_camera_0[0:3, 0:3]
    t = T_camera_0[0:3, 3:4]
    
  if origin:
    if numpy.abs(numpy.array(llh)-origin).max() > eps:
      raise Exception('Origins not the same. Code missing')      
  return (K_i, R, t, llh)

def get_llh(image, camera_set_id):
  import voxel_globe.tools.enu as enu

  (k,r,t,origin)= get_krt(image, camera_set_id)
  cameraCenter = -r.T.dot(t)
  
  llh =  enu.enu2llh(lon_origin=origin[0], 
                     lat_origin=origin[1], 
                     h_origin=origin[2], 
                     east=cameraCenter[0], 
                     north=cameraCenter[1], 
                     up=cameraCenter[2])
  
  return (llh['lon'][0], llh['lat'][0], llh['h'][0])

def get_kto(image, camera_set_id=None):
  ''' OLD! Use get_krt returns K, T, llh_origin (lon, lat, h)'''
  debug= 0
  
  if camera_set_id:
    camera = image.camera_set.get(cameraset=camera_set_id)
  else:
    #TOTAL HACK Camera sets need to be fully plumbed. This prevents multiple cameras per image for now
    camera = image.camera_set.all()[0]
  if debug:
    print "Camera"
    print repr(camera)
  K_i = numpy.eye(3)
  K_i[0,2] = camera.principal_point[0]
  K_i[1,2] = camera.principal_point[1]
  K_i[0,0] = camera.focal_length[0]
  K_i[1,1] = camera.focal_length[1]
  
  llh = [None]
  
  coordinate_systems = [camera.coordinate_system]
  if debug:
    print "CS1"
    print repr(coordinate_systems)  
  coordinate_transforms = []
  while len(coordinate_systems[0].coordinatetransform_to_set.all()):
    #While the first coordinate system has a transform, pre-pend it to the list
    ct = coordinate_systems[0].coordinatetransform_to_set.all().select_subclasses()[0]
    if debug:
      print "CT"
      print repr(ct)
    #cs = ct.coordinate_system_from.get_subclasses()[0]
    cs = ct.coordinate_system_from.select_subclasses()[0]
    if debug:
      print "CS"
      print repr(cs)
    coordinate_transforms = [ct]+coordinate_transforms
    coordinate_systems = [cs] + coordinate_systems
  
  if isinstance(coordinate_systems[0], models.GeoreferenceCoordinateSystem):
    llh = list(coordinate_systems[0].location)
    if debug:
      print "llh"
      print llh
  
  T_camera_0 = numpy.eye(4)
  for ct in coordinate_transforms:
    T = numpy.eye(4)
    T[0,0:3] = ct.rodriguezX
    T[1,0:3] = ct.rodriguezY
    T[2,0:3] = ct.rodriguezZ
    T[0:3, 3] = ct.translation
    T_camera_0 = T.dot(T_camera_0)
    
  if debug:
    print 'Final T'
    print T_camera_0
    
  return (K_i, T_camera_0, llh)
