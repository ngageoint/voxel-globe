import numpy
import voxel_globe.meta.models
import inspect

def projectPoint(K, T, llh_xyz, xs, ys, distances=None, zs=None):
  ''' Project a set of points xs, ys (Nx1 numpy array each) through the K (3x3) T (4x4) 
      model at llh_xyz (3x1). You must either specify the distances to project
      (scalar) or the z intersection planes (scalar)
      
      returns dictionary with lon, lat, h'''
  import voxel_globe.tools.enu as enu;
  
  debug = 0;
  
  if debug:
    print 'xyz', xs,ys,zs

  R = T[0:3, 0:3];
  t = T[0:3, 3:]; #Extract 3x1, which is why the : is necessary
  cam_center = -R.T.dot(t);
  if debug:
    print 'Cam_center', cam_center
  P = K.dot(numpy.concatenate((R,t), axis=1));
  Pi = numpy.matrix(P).I;
  if debug:
    print 'P'
    print repr(P)
    print numpy.linalg.pinv(P)
    print 'Pi', Pi
    print [xs,ys,numpy.ones(xs.shape)]
  ray = numpy.array(Pi).dot([xs,ys,numpy.ones(xs.shape)]);
  if debug:
    print 'ray is currently', ray
  


  if abs(ray[3,0]) < 1e-6:
    ray = cam_center + ray[0:3,0:]
  else:
    ray = ray[0:,:]/ray[3,:]; #dehomoginize
  
  if debug:
    print llh_xyz
    print 'ray was', ray
  
  #dp = (P[2:3,:].T * ray[:]).sum(axis=0);
  # Principal plane dot ray
  # NOT WORKING
  #if ray[3] < 0:
  #  dp *= -1;
  #print 'dot',dp 

  ray = cam_center-ray[0:3,:]


  for c in range(ray.shape[1]):
    if distances is None:
      t = (zs - llh_xyz[2] - cam_center[2])/ray[2,c]; #project to sea level
    else:
      t = -distances / numpy.linalg.norm(ray[:,c]);
      #WHY is that minus sign there? Tried the dot product test above, didn't help
    if debug:
      print 't', t
      print 'cam_center', cam_center
    ray[:,c:c+1] = ray[:,c:c+1] * t + cam_center;
  if debug:
    print 'ray is now', ray 

  llh2_xyz = enu.enu2llh(lon_origin=llh_xyz[0], 
                         lat_origin=llh_xyz[1], 
                         h_origin=llh_xyz[2], 
                         east=ray[0,:], 
                         north=ray[1,:], 
                         up=ray[2,:])
  return llh2_xyz
