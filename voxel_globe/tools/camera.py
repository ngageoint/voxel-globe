import logging
logger = logging.getLogger();

import numpy
from django.contrib.gis.geos import Point

import voxel_globe.meta.models as models

def save_krt(service_id, image, k, r, t, origin, srid=4326):
  '''Saves the appropriate krt model to the image
  
     Keyword Arguments:
     service_id - Id field from the celery task calling this function
     image - voxel_globe.meta.Image object or object_id number
     k - 3x3 numpy.array
     r - 3x3 numpy.array
     t - 3 numpy.array
     origin - 3 numpy.arry, longitude, latitude, altitude in xyz order
     srid - srid number for origin
  '''

  if not hasattr(image, 'name'): #duck type, for maximum flexibility
    image =  models.Image.objects.get(id=image)

#  (k,r,t) = cam.krt(width=image.imageWidth, height=image.imageHeight);
  logger.info('Origin is %s' % str(origin))

  grcs = models.GeoreferenceCoordinateSystem.create(
                  name='%s 0' % image.name,
                  xUnit='d', yUnit='d', zUnit='m',
                  location='SRID=%d;POINT(%0.15f %0.15f %0.15f)' 
                            % (srid, origin[0], origin[1], origin[2]),
                  service_id = service_id)
  grcs.save()
  cs = models.CartesianCoordinateSystem.create(
                  name='%s 1' % (image.name),
                  service_id = service_id,
                  xUnit='m', yUnit='m', zUnit='m');
  cs.save()

  transform = models.CartesianTransform.create(
                       name='%s 1_0' % (image.name),
                       service_id = service_id,
                       rodriguezX=Point(*r[0,:]),
                       rodriguezY=Point(*r[1,:]),
                       rodriguezZ=Point(*r[2,:]),
                       translation=Point(t[0], t[1], t[2]),
                       coordinateSystem_from_id=grcs.id,
                       coordinateSystem_to_id=cs.id)
  transform.save()

  camera = image.camera;
  try:
    camera.update(service_id = service_id,
                  focalLengthU=k[0,0],   focalLengthV=k[1,1],
                  principalPointU=k[0,2], principalPointV=k[1,2],
                  coordinateSystem=cs);
  except:
    camera = models.Camera.create(name=image.name,
                  service_id = service_id,
                  focalLengthU=k[0,0],   focalLengthV=k[1,1],
                  principalPointU=k[0,2], principalPointV=k[1,2],
                  coordinateSystem=cs);
    camera.save();
    image.update(camera = camera);

def get_krt(image, origin=None, history=None, eps=1e-9):
  ''' returns K, T, llh_origin (lon, lat, h)'''
  camera = image.camera.history(history);
  K_i = numpy.eye(3);
  K_i[0,2] = camera.principalPointU;
  K_i[1,2] = camera.principalPointV;
  K_i[0,0] = camera.focalLengthU;
  K_i[1,1] = camera.focalLengthV;
  
  llh = [None];
  
  coordinate_systems = [camera.coordinateSystem.history(history)]
  coordinate_transforms = [];
  while len(coordinate_systems[0].coordinatetransform_to_set.all()):
    #While the first coordinate system has a transform, pre-pend it to the list
    ct = coordinate_systems[0].coordinatetransform_to_set.all()[0].history(history);

    #cs = ct.coordinateSystem_from.get_subclasses()[0];
    cs = ct.coordinateSystem_from.history(history);
    coordinate_transforms = [ct]+coordinate_transforms;
    coordinate_systems = [cs] + coordinate_systems;
  
  if isinstance(coordinate_systems[0], models.GeoreferenceCoordinateSystem):
    llh = list(coordinate_systems[0].history(history).location);
  
  T_camera_0 = numpy.eye(4);
  for ct in coordinate_transforms:
    T = numpy.eye(4);
    T[0,0:3] = ct.rodriguezX;
    T[1,0:3] = ct.rodriguezY;
    T[2,0:3] = ct.rodriguezZ;
    T[0:3, 3] = ct.translation;
    T_camera_0 = T.dot(T_camera_0);
    
    R = T_camera_0[0:3, 0:3];
    t = T_camera_0[0:3, 3:4];
    
  if origin:
    if numpy.abs(numpy.array(llh)-origin).max() > eps:
      pass#Convert to different origin. WARNING, less stable
  return (K_i, R, t, llh);

def get_llh(image, history=None):
  import voxel_globe.tools.enu as enu

  (k,r,t,origin)= get_krt(image, history=history)
  cameraCenter = -r.T.dot(t)
  
  llh =  enu.enu2llh(lon_origin=origin[0], 
                     lat_origin=origin[1], 
                     h_origin=origin[2], 
                     east=cameraCenter[0], 
                     north=cameraCenter[1], 
                     up=cameraCenter[2])
  
  return (llh['lon'][0], llh['lat'][0], llh['h'][0])

def get_kto(image, history=None):
  ''' OLD! Use get_krt returns K, T, llh_origin (lon, lat, h)'''
  debug= 0;
  
  camera = image.camera.history(history);
  if debug:
    print "Camera"
    print repr(camera);
  K_i = numpy.eye(3);
  K_i[0,2] = camera.principalPointU;
  K_i[1,2] = camera.principalPointV;
  K_i[0,0] = camera.focalLengthU;
  K_i[1,1] = camera.focalLengthV;
  
  llh = [None];
  
  coordinate_systems = [camera.coordinateSystem.history(history)]
  if debug:
    print "CS1"
    print repr(coordinate_systems)  
  coordinate_transforms = [];
  while len(coordinate_systems[0].coordinatetransform_to_set.all()):
    #While the first coordinate system has a transform, pre-pend it to the list
    ct = coordinate_systems[0].coordinatetransform_to_set.all()[0].history(history);
    if debug:
      print "CT"
      print repr(ct)
    #cs = ct.coordinateSystem_from.get_subclasses()[0];
    cs = ct.coordinateSystem_from.history(history);
    if debug:
      print "CS"
      print repr(cs)
    coordinate_transforms = [ct]+coordinate_transforms;
    coordinate_systems = [cs] + coordinate_systems;
  
  if isinstance(coordinate_systems[0], models.GeoreferenceCoordinateSystem):
    llh = list(coordinate_systems[0].history(history).location);
    if debug:
      print "llh"
      print llh
  
  T_camera_0 = numpy.eye(4);
  for ct in coordinate_transforms:
    T = numpy.eye(4);
    T[0,0:3] = ct.rodriguezX;
    T[1,0:3] = ct.rodriguezY;
    T[2,0:3] = ct.rodriguezZ;
    T[0:3, 3] = ct.translation;
    T_camera_0 = T.dot(T_camera_0);
    
  if debug:
    print 'Final T'
    print T_camera_0
    
  return (K_i, T_camera_0, llh);
