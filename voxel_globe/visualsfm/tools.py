import subprocess
#from subprocess import Popen
from voxel_globe.tools.celery import Popen

import numpy as np;
from osgeo.gdal import GCP
import os

class Image(object):
  def __init__(self, line=None, name=None, focalLength=None, 
               rotation_wxyz=[1,0,0,0], 
               translation_xyz=[0,0,0], 
               radialDistortion=[0,0]):
    ''' line - string from nvm file 
        or
        name - image filename
        focalLength (optional) - focal length in pixels
        camera (optional) - 10 numbers to represent camera '''
    if line:
      (self.name, camera) = line.split('\t')
      self.name = self.name.replace('"', ' ');
      camera = camera.strip();
      camera = np.array(map(float, camera.split(' ')));
      self.focalLength = camera[0]
      self.rotation_wxyz = camera[1:5]/np.linalg.norm(camera[1:5]);
      self.translation_xyz = camera[5:8];
      self.radialDistortion = camera[8:];
    else:
      self.name = name
      if focalLength:
        self.focalLength = focalLength
      else:
        from PIL import Image;
        img = Image.open(self.name)
        self.focalLength = 1.2 * max(img.size); #param_default_focal_ratio
        img.close();
      self.rotation_wxyz = rotation_wxyz;
      self.translation_xyz = translation_xyz;
      self.radialDistortion = radialDistortion

  def __str__(self):
    return self.name.replace(' ', '"')+'\t' + ('%0.12g '*10) % (
                  (self.focalLength,)+
                  tuple(self.rotation_wxyz)+
                  tuple(self.translation_xyz)+
                  tuple(self.radialDistortion))

  def __repr__(self):
    return '''Filename: %s
FocalLength: %f
R: %s
T: %s
rd: %s''' % (self.name, self.focalLength, 
             str(self.rotation_wxyz), 
             str(self.translation_xyz), 
             str(self.radialDistortion))

  ''' General use:
    1) generateMatchPoints
    '''

  def krt(self, width=0, height=0):
    k = np.eye(3);
    k[0,0] = self.focalLength;
    k[1,1] = self.focalLength;
    k[0,2] = width/2;
    k[1,2] = height/2;

    w2 = self.rotation_wxyz[0]**2;
    x2 = self.rotation_wxyz[1]**2;
    y2 = self.rotation_wxyz[2]**2;
    z2 = self.rotation_wxyz[3]**2;
    wx = self.rotation_wxyz[0]*self.rotation_wxyz[1];
    wy = self.rotation_wxyz[0]*self.rotation_wxyz[2];
    wz = self.rotation_wxyz[0]*self.rotation_wxyz[3];
    xy = self.rotation_wxyz[1]*self.rotation_wxyz[2];
    xz = self.rotation_wxyz[1]*self.rotation_wxyz[3];
    yz = self.rotation_wxyz[2]*self.rotation_wxyz[3];

# This was a "unit quaternion" version of the equation from wiki
#     r = np.array([[1-2*y2-2*z2, 2*xy-2*wz,   2*xz+2*wy],
#                   [2*xy+2*wz,   1-2*x2-2*z2, 2*yz-2*wx],
#                   [2*xz-2*wy,   2*yz+2*wx,   1-2*x2-2*y2]])
#     
#       T x2 = x() * x(),  xy = x() * y(),  rx = r() * x(),
#     y2 = y() * y(),  yz = y() * z(),  ry = r() * y(),
#     z2 = z() * z(),  zx = z() * x(),  rz = r() * z(),
#     r2 = r() * r();
#   vnl_matrix_fixed<T,3,3> rot;
#   rot(0,0) = r2 + x2 - y2 - z2;         // fill diagonal terms
#   rot(1,1) = r2 - x2 + y2 - z2;
#   rot(2,2) = r2 - x2 - y2 + z2;
#   rot(0,1) = 2 * (xy + rz);             // fill off diagonal terms
#   rot(0,2) = 2 * (zx - ry);
#   rot(1,2) = 2 * (yz + rx);
#   rot(1,0) = 2 * (xy - rz);
#   rot(2,0) = 2 * (zx + ry);
#   rot(2,1) = 2 * (yz - rx);

    r = np.array([[w2+x2-y2-z2, 2*(xy-wz),   2*(wy+xz)],
                  [2*(wz+xy),   w2-x2+y2-z2, 2*(yz-wx)],
                  [2*(xz-wy),   2*(wx+yz),   w2-x2-y2+z2]])

    t = np.array(self.translation_xyz); #currently in world coordinates
    t.shape = (3,1);
    t = -r.dot(t)
    return (k,r,t);
  
  def to_text_file_format(self, enu_center = None, filename=None, width=0, height=0):
    ''' temp function to use preexisting import for testing
        purposes. DELETE ME when ready '''
    (k,r,t) = self.krt(width, height);
    
    T = np.eye(4);
    T[0:3,0:3] = r;
    T[0:3,3:] = t;
    K=[k[0,0], k[1,1], k[0,2], k[1,2]];
    
    return "'%s', %s, %s, %s" % (filename, 
                                 str([enu_center['lon'], enu_center['lat'], enu_center['h']]),
                                 str(T.tolist()),
                                 str(K))
    

  def vip_camera(self):
    ''' returns a translation matrix and K matrix???'''
    return None;

def writeNvm(images, outputNvm):
  ''' images - list of N Image's
      outputNvm - output file name '''
  
  with open(outputNvm, 'w') as fid:
    fid.write('''NVM_V3 

%d
''' % len(images))
  
    for image in images:
      fid.write(str(image) + '\n')
    fid.write('''0

0

#the last part of NVM file points to the PLY files
#the first number is the number of associated PLY files
#each following number gives a model-index that has PLY
0
''')

def readNvm(inputNvm):
  with open(inputNvm, 'r') as fid:
    assert(fid.readline().startswith('NVM_V3'))
    fid.readline();
    numberCameras= int(fid.readline());
    cameras = [];
    for i in range(numberCameras):
      cameras.append(Image(fid.readline()))
      
  return cameras;

def writeGcpFile(inputs, outputGps):
  ''' inputs - List of objcets, with .filename and .xyz fields, in degree/meters
      outputGps - output gps filename '''
  with open(outputGps, 'w') as fid:
    for input in inputs:
      fid.write(input['filename'] + 
                (' %0.12g'*3) % (input['xyz'][0], input['xyz'][1], input['xyz'][2]) +'\n');

def writeGcpFileEcef(inputs, outputGps):
  ''' Same as writeGpsFile, except ecef
      inputs - List of objcets, with .filename and .llh_xyz fields, in degree/meters
      outputGps - output gcp filename '''
  import voxel_globe.tools.enu as enu

  with open(outputGps, 'w') as fid:
    for input in inputs:
      ecef_xyz = enu.llh2xyz(lat=input.llh_xyz[1], 
                         lon=input.llh_xyz[0], 
                         h=input.llh_xyz[2])
      fid.write(input.filename + 
                (' %0.12g'*3) % ecef_xyz +'\n');

def writeGcpFileEnu(inputs, outputGps, lat_origin, lon_origin, h_origin):
  ''' Same as writeGpsFile, except enu
      inputs - List of objcets, with .filename and .llh_xyz fields, in degree/meters
      outputGps - output gcp filename 
      lat_origin, lon_origin, h_origin 
        - origin of enu cooridinate system, in degrees/meters'''

  import voxel_globe.tools.enu as enu

  with open(outputGps, 'w') as fid:
    for input in inputs:
      enu_xyz = enu.llh2enu(lat=input.llh_xyz[1], 
                            lon=input.llh_xyz[0], 
                            h=input.llh_xyz[2],
                            lat_origin=lat_origin, 
                            lon_origin=lon_origin,
                            h_origin=h_origin)
      fid.write(input.filename + 
                (' %0.12g'*3) % enu_xyz +'\n');

def runVisualSfm(sfmArg='sfm', args=[], logger=None):
  return Popen([runVisualSfm.program, sfmArg] + args, logger=logger, shell=False)
  #I thought shell=True was IMPORTANT, or else visual sfm crashes becuase of the stdout/stderr
  #redirect. I didn't know why, I assumed he was trying to be clever about something, does 
  #something non-standard AND CRASHES! Now I think it's just an issue of if the program starts
  #and stdout/stderr aren't being read from right away, it fails. This is probably due to the
  #fact that one executable is both a CLI and non-CLI, which is not straightforward in windows
  #like it is in linux. 
runVisualSfm.program = os.environ['VIP_VISUALSFM_EXE'] 

def generateMatchPoints(inputs, outputNvm, matchArg=None, logger=None):
  ''' Generate match 
      inputs - list of files names
      outputNvm - name of output NVM file '''

  images = [];
  
  for input in inputs:
    images += [Image(name=input)];
    
  writeNvm(images, outputNvm)

  sfmArg = 'sfm';
  args = [outputNvm]
  if matchArg:
    sfmArg += '+pairs';
    args += [matchArg];
  sfmArg+='+skipsfm'
  
  runVisualSfm(sfmArg, args, logger).wait();

def runSparse(inputNvm, outputNvm, shared=True, gcp=False, logger=None):
  sfmArg = 'sfm';
  if shared:
    sfmArg+='+shared'
  if gcp:
    sfmArg+='+gcp'
    #optionally verify inputNvm.gcp exists here
  
  runVisualSfm(sfmArg, [inputNvm, outputNvm], logger).wait();

# def runDesnse(inputNvm, outputNvm, shared=True, skipPmvs=False):
#   sfmArg = 'sfm';
#   if shared:
#     sfmArg+='+shared'
#   sfmArg += '+'
#   
#   runVisualSfm('sfm', [inputNvm, outputNvm]);
#   