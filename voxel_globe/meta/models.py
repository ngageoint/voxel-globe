from django.contrib.gis.db import models
from django.core.exceptions import FieldError
from django.db.transaction import atomic
from django.db.models.fields.related import OneToOneField
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User

from model_utils.managers import InheritanceManager

class InheritanceGeoManager(InheritanceManager, models.GeoManager):
  pass

import json

from uuid import uuid4

import numpy as np

import os

# Create your models here.

PIXEL_FORMAT = map(np.dtype, sum(np.sctypes.values(), []))
PIXEL_FORMAT = zip(map(lambda x: x.char, PIXEL_FORMAT), 
                   map(lambda x: x.name, PIXEL_FORMAT))
#Basically, V is the other (so Two Ration Ints is an other case), 
#while O is a python object other, probably not of concern  

LENGTH_UNIT = (('m', 'Meters'), ('f', 'Feet'))
ANGLE_UNIT = (('r', 'Radians'), ('d', 'Degrees'))

use_geography_points = False

@python_2_unicode_compatible #only needed on subclasses that define __str__
class VipCommonModel(models.Model):
  class Meta:
    abstract = True

  objects = InheritanceManager()
  def select_subclasses(self):
#    print "BAD BAD BAD! THIS SHOULDN'T BE USED! USE THIS TO KNOW WHAT NEEDS TO BE FIXED!!!"
#    print "You should be using more .filter[0] and less .get to get rid of this"
    return self._meta.model.objects.filter(id=self.id).select_subclasses()

  #Returns the string representation of the model
  def __str__(self):
    return '%s[%s]' % (self.name, self.id)
  
  def __repr__(self, recurse=0, indent=0):
    s = ''
    for field in self._meta.fields:
      fieldName = field.name
      try:
        fieldValue = getattr(self, fieldName)
      except: # field.rel.to.DoesNotExist: While this WORKS, I do not understand it, so I will not use it
        fieldValue = "Error: Does Not Exist"
      if isinstance(fieldValue, models.Model):
        if recurse and isinstance(fieldValue, VipCommonModel):
          s += ' '*indent+'%s:\n' % (fieldName)
          s += fieldValue.__repr__(indent=indent+4, recurse=recurse-1)
        else:
          s += ' '*indent+'%s: %s - %s\n' % (fieldName, fieldValue._meta.model_name, unicode(fieldValue))
      else:
        s += ' '*indent+'%s: %s\n' % (fieldName, fieldValue)
        
    for field in self._meta.many_to_many:
      fieldName = field.name
      s += ' '*indent+'%s\n' % fieldName
      try:
        fieldValues = getattr(self, fieldName).all()
      except:
        fieldValues = []
      for m2m in fieldValues:
        if recurse and isinstance(m2m, VipCommonModel):
          s += ' '*(indent+1)+'%s\n' % m2m
          s += m2m.__repr__(indent=indent+2, recurse=recurse-1)
        else:
          s += ' '*(indent+2)+'%s\n' % m2m
    return s

@python_2_unicode_compatible
class ServiceInstance(VipCommonModel):
  inputs = models.TextField('Inputs')
  outputs = models.TextField('Outputs')
  
  #inputId m2m generic foreign key
  #outputId m2m generic foreign key
  
  # TODO remove null=True, blank=True
  user = models.ForeignKey(User, null=True, blank=True)
  entry_time = models.DateTimeField(auto_now_add = True)
  finish_time = models.DateTimeField(auto_now = True)
  
  status = models.CharField(max_length=32)
  
  service_name = models.CharField(max_length=128)
  
  def __str__(self):
    return '%s [%s]' % (self.service_name, self.id)

#Abstract common model - GOOD inheritance
class VipObjectModel(VipCommonModel):
  service = models.ForeignKey('ServiceInstance', blank=True, null=True)
  name = models.TextField()
  _attributes = models.TextField(default='', blank=True)

  @property
  def attributes(self):
    try:
      return json.loads(self._attributes)
    except ValueError:
      return dict()

  @attributes.setter
  def attributes(self, value):
    self._attributes = json.dumps(value)

  class Meta:
    abstract = True

#TODO: Make this a perspective camera and inherit from Camera, make Camera an abstract class. BIG refactor!!!
class Camera(VipObjectModel):
  focal_length = models.PointField(dim=2, null=True, blank=True)
  principal_point = models.PointField(dim=2, null=True, blank=True)
  coordinate_system = models.ForeignKey('CoordinateSystem', null=True, blank=True)
  image = models.ForeignKey('Image')

class CameraSet(VipObjectModel):
  cameras = models.ManyToManyField('Camera')
  images = models.ForeignKey('ImageSet', related_name='cameras')

''' Coordinate systems '''
#this is where the inheritance becomes less good... I worked around it, but still...
class CoordinateSystem(VipObjectModel):
  pass

class CartesianCoordinateSystem(CoordinateSystem):
  x_unit = models.CharField(max_length=1, choices=LENGTH_UNIT)
  y_unit = models.CharField(max_length=1, choices=LENGTH_UNIT)
  z_unit = models.CharField(max_length=1, choices=LENGTH_UNIT)

class GeoreferenceCoordinateSystem(CoordinateSystem):
  x_unit = models.CharField(max_length=1, choices=LENGTH_UNIT+ANGLE_UNIT)
  y_unit = models.CharField(max_length=1, choices=LENGTH_UNIT+ANGLE_UNIT)
  z_unit = models.CharField(max_length=1, choices=LENGTH_UNIT+ANGLE_UNIT)
  location = models.PointField(dim=3)
  
  objects = InheritanceGeoManager()
  #I need a GeoManager for PostGIS objects

''' Coordinate Transforms '''

class CoordinateTransform(VipObjectModel):
  coordinate_system_from = models.ForeignKey('CoordinateSystem', related_name='coordinatetransform_from_set')
  coordinate_system_to   = models.ForeignKey('CoordinateSystem', related_name='coordinatetransform_to_set')

class CartesianTransform(CoordinateTransform):
  #rodriguez = models.PointField(dim=3)
  rodriguezX = models.PointField(dim=3)
  rodriguezY = models.PointField(dim=3)
  rodriguezZ = models.PointField(dim=3)
  #TOTAL HACK until I get REAL Rodriguez vectors in here, I will Store R!

  translation = models.PointField(dim=3)

''' The rest '''

class Image(VipObjectModel):
  file_format = models.CharField(max_length=4)
  pixel_format = models.CharField(max_length=1, choices=PIXEL_FORMAT)

  image_width = models.PositiveIntegerField('Image Width (pixels)')
  image_height = models.PositiveIntegerField('Image Height (pixels)')
  number_bands = models.PositiveIntegerField('Number of Color Bands')
  _filename_path = models.TextField()

  @property
  def filename_path(self):
    return os.path.expandvars(self._filename_path)

  @filename_path.setter
  def filename_path(self, value):
    from vsi.tools.dir_util import is_subdir
    import posixpath
    storage = is_subdir(value, os.environ['VIP_STORAGE_DIR'])
    if storage[0]:
      value = posixpath.join('${VIP_STORAGE_DIR}',
                             posixpath.normpath(storage[1]))
    else:
      image = is_subdir(value, os.environ['VIP_IMAGE_DIR'])
      if image[0]:
        value = posixpath.join('${VIP_IMAGE_DIR}',
                               posixpath.normpath(image[1]))
      else:
        value = posixpath.normpath(value)

    self._filename_path = value

  @property
  def filename_url(self):
    if os.environ['VIP_IMAGE_SERVER_DIFFERENT'] == '0':
      image_url = self._filename_path.replace('${VIP_IMAGE_DIR}',
          '%s' % os.environ['VIP_IMAGE_SERVER_URL_PATH'])
    else:
      image_url = self._filename_path.replace('${VIP_IMAGE_DIR}',
          '%s://%s:%s%s' % (os.environ['VIP_IMAGE_SERVER_PROTOCOL'],
                            os.environ['VIP_IMAGE_SERVER_HOST'],
                            os.environ['VIP_IMAGE_SERVER_PORT'],
                            os.environ['VIP_IMAGE_SERVER_URL_PATH']))

    return image_url

  @property
  def zoomify_path(self):
    filename = os.path.join(os.path.dirname(self.filename_path), 'zoomify')
    return filename

  @property
  def zoomify_url(self):
    filename = '/'.join((os.path.dirname(self._filename_path), 'zoomify/'))

    if os.environ['VIP_IMAGE_SERVER_DIFFERENT'] == '0':
      image_url = filename.replace('${VIP_IMAGE_DIR}',
          '%s' % os.environ['VIP_IMAGE_SERVER_URL_PATH'])
    else:
      image_url = filename.replace('${VIP_IMAGE_DIR}',
          '%s://%s:%s%s' % (os.environ['VIP_IMAGE_SERVER_PROTOCOL'],
                            os.environ['VIP_IMAGE_SERVER_HOST'],
                            os.environ['VIP_IMAGE_SERVER_PORT'],
                            os.environ['VIP_IMAGE_SERVER_URL_PATH']))
    return image_url

  readonly_fields = ('zoomify_url', 'filename_url')

  acquisition_date = models.DateTimeField(blank=True, null=True)
  coverage_poly = models.PolygonField(blank=True, null=True)

  class Meta:
    ordering=('name',)
    #Temporary fix, until I get a through class working

class ImageSet(VipObjectModel):
  images = models.ManyToManyField('Image')
  scene = models.ForeignKey('Scene', blank=True, null=True)

class TiePoint(VipObjectModel):
  #description = models.CharField(max_length=250)
  #x = models.FloatField()
  #y = models.FloatField()
  point = models.PointField(dim=2)
  
  image = models.ForeignKey('Image', blank=False)
  control_point = models.ForeignKey('ControlPoint', null=True, blank=True)

  objects = InheritanceGeoManager()

class TiePointSet(VipObjectModel):
  tie_points = models.ManyToManyField('TiePoint')

class ControlPoint(VipObjectModel):
  description = models.TextField()

  point = models.PointField(dim=3, geography=use_geography_points)
  original_point = models.PointField(dim=3, null=True, blank=True)
  original_srid = models.IntegerField(null=True, blank=True)

  objects = InheritanceGeoManager()

@python_2_unicode_compatible
class Scene(VipObjectModel):
  origin = models.PointField(dim=3, null=False, blank=False)
  geolocated = models.BooleanField(default=True) #REFACT: Remove the default, make required
  bbox_min = models.PointField(dim=3, default='POINT(0 0 0)')#REFACT: , null=False, blank=False)
  bbox_max = models.PointField(dim=3, default='POINT(0 0 0)')#REFACT: , null=False, blank=False)
  default_voxel_size = models.PointField(dim=3, default='POINT(0 0 0)')#REFACT: , null=False, blank=False)
  
  def __str__(self):
    return '%s [%s]' % (self.name, self.origin)

@python_2_unicode_compatible
class VoxelWorld(VipObjectModel):
  origin = models.PointField(dim=3, geography=use_geography_points, null=False, blank=False)
  directory = models.TextField()
  def __str__(self):
    return '%s [%s]' % (self.name, self.origin)

@python_2_unicode_compatible
class PointCloud(VipObjectModel):
  origin = models.PointField(dim=3, geography=use_geography_points, null=False, blank=False)
  _filename_path = models.TextField()
  _potree_dir = models.TextField() #The url for Potree

  @property
  def filename_path(self):
    return os.path.expandvars(self._filename_path)

  @filename_path.setter
  def filename_path(self, value):
    from vsi.tools.dir_util import is_subdir
    import posixpath
    storage = is_subdir(value, os.environ['VIP_STORAGE_DIR'])
    if storage[0]:
      value = posixpath.join('${VIP_STORAGE_DIR}',
                             posixpath.normpath(storage[1]))
    else:
      image = is_subdir(value, os.environ['VIP_IMAGE_DIR'])
      if image[0]:
        value = posixpath.join('${VIP_IMAGE_DIR}',
                               posixpath.normpath(image[1]))
      else:
        value = posixpath.normpath(value)

    self._filename_path = value

  @property
  def potree_dir(self):
    return os.path.expandvars(self._potree_dir)

  @potree_dir.setter
  def potree_dir(self, value):
    from vsi.tools.dir_util import is_subdir
    import posixpath
    storage = is_subdir(value, os.environ['VIP_STORAGE_DIR'])
    if storage[0]:
      value = posixpath.join('${VIP_STORAGE_DIR}',
                             posixpath.normpath(storage[1]))
    else:
      image = is_subdir(value, os.environ['VIP_IMAGE_DIR'])
      if image[0]:
        value = posixpath.join('${VIP_IMAGE_DIR}',
                               posixpath.normpath(image[1]))
      else:
        value = posixpath.normpath(value)

    self._potree_dir = value

  @property
  def potree_url(self):
    filename = '/'.join((self._potree_dir, 'cloud.js'))

    if os.environ['VIP_IMAGE_SERVER_DIFFERENT'] == '0':
      image_url = filename.replace('${VIP_IMAGE_DIR}',
          '%s' % os.environ['VIP_IMAGE_SERVER_URL_PATH'])
    else:
      image_url = filename.replace('${VIP_IMAGE_DIR}',
          '%s://%s:%s%s' % (os.environ['VIP_IMAGE_SERVER_PROTOCOL'],
                            os.environ['VIP_IMAGE_SERVER_HOST'],
                            os.environ['VIP_IMAGE_SERVER_PORT'],
                            os.environ['VIP_IMAGE_SERVER_URL_PATH']))
    
    return image_url

  readonly_fields = ('potree_url',)

  def __str__(self):
    return '%s [%s]' % (self.name, self.origin)

#@python_2_unicode_compatible
#class FileObject(object):
#  pass
#
#@python_2_unicode_compatible
#class DirectoryObject(object):
#  pass

@python_2_unicode_compatible
class SattelSite(VipObjectModel):
  bbox_min = models.PointField(dim=3, null=False, blank=False)
  bbox_max = models.PointField(dim=3, null=False, blank=False)
  image_set = models.ForeignKey('ImageSet', null=True) #remove null=True
  camera_set = models.ForeignKey('CameraSet', null=True) #remove null=True
  def __str__(self):
    return '%s [%s-%s]' % (self.name, self.bbox_min, self.bbox_max)

@python_2_unicode_compatible
class SattelGeometryObject(VipObjectModel):
  description = models.TextField(null=True, blank=True)
  origin = models.PointField(dim=3, null=False, blank=False)
  geometry_path = models.TextField('Geometry Filename', null=True, blank=True)
  geometry = models.PolygonField(dim=3, default='POLYGON((0 0 0, 0 0 0, 0 0 0, 0 0 0))')
  height = models.FloatField(default=0.0)
  site = models.ForeignKey('SattelSite', null=False, blank=False)
      #Do we NEED this too?
  def __str__(self):
    return self.name


@python_2_unicode_compatible
class SattelEventTrigger(VipObjectModel):
  description = models.TextField(null=True, blank=True)
  origin = models.PointField(dim=3, default='POINT(0 0 0)', null=False, blank=False)
  event_areas = models.ManyToManyField('SattelGeometryObject', default=[], blank=True, related_name='event_event_trigger')
  reference_areas = models.ManyToManyField('SattelGeometryObject', default=[], blank=True, related_name='reference_event_trigger')
  reference_image = models.ForeignKey('Image')
  site = models.ForeignKey('SattelSite', null=False, blank=False)
  def __str__(self):
    return self.name

@python_2_unicode_compatible
class SattelEventResult(VipObjectModel):
  geometry = models.ForeignKey('SattelGeometryObject', null=False, blank=False)
  score = models.FloatField(null=False, blank=False)
  reference_image = models.ForeignKey('Image', related_name='reference_event_result')
  mission_image = models.ForeignKey('Image', related_name='mission_event_result')
  def __str__(self):
    return self.name

@python_2_unicode_compatible
class RpcCamera(Camera):
  rpc_path = models.TextField('Geometry Filename', null=False, blank=False)

  def __str__(self):
    return self.name
