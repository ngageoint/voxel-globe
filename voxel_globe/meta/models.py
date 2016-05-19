from django.contrib.gis.db import models
from django.core.exceptions import FieldError
from django.db.transaction import atomic
from django.db.models.fields.related import OneToOneField
from django.utils.encoding import python_2_unicode_compatible

from model_utils.managers import InheritanceManager

class InheritanceGeoManager(InheritanceManager, models.GeoManager):
  pass

import json

from uuid import uuid4

import numpy as np

# Create your models here.

PIXEL_FORMAT = map(np.dtype, sum(np.sctypes.values(), []))
PIXEL_FORMAT = zip(map(lambda x: x.char, PIXEL_FORMAT), 
                   map(lambda x: x.name, PIXEL_FORMAT))
#Basically, V is the other (so Two Ration Ints is an other case), 
#while O is a python object other, probably not of concern  

LENGTH_UNIT = (('m', 'Meters'), ('f', 'Feet'))
ANGLE_UNIT = (('r', 'Radians'), ('d', 'Degrees'))
COORDINATE_SYSTEM = (('l', 'Local Vertical Coordinate System'),
                     ('c', 'Cartesian'))
TRANSFORMATION_TYPE = (('c', 'Cartesian'),
                       ('s', 'Similarity'),
                       ('g', 'Geographic'))

MODEL_TYPE = (('vol', 'Volumentric'), ('ph', 'Polyhedral'), ('pl', 'Plane'),
              ('c', 'Cylinder'), ('pc', 'Point Cloud'))

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

  #def get_subclasses(self):
  #  rels = [rel.model.objects.filter(id=self.id) for rel in self._meta.get_all_related_objects()
  #    if isinstance(rel.field, OneToOneField)
  #    and issubclass(rel.field.model, self._meta.model)
  #    and self._meta.model is not rel.field.model]
  #  rels = [rel[0] for rel in rels
  #          if len(rel)]
  #  return rels

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
  
  user = models.CharField(max_length=32)
  entryTime = models.DateTimeField(auto_now_add = True)
  finishTime = models.DateTimeField(auto_now = True)
  
  status = models.CharField(max_length=32)
  
  serviceName = models.CharField(max_length=128)
  
  def __str__(self):
    return '%s [%s]' % (self.serviceName, self.id)

#Abstract common model - GOOD inheritance
class VipObjectModel(VipCommonModel):
  service = models.ForeignKey('ServiceInstance')
  name = models.TextField()
  _attributes = models.TextField(default='')

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

  @classmethod
  def taskAddSync(cls, *args, **kwargs):
    ''' I believe this function was suppose to ease creating objects (for development)
        without having to use services all the time.
        This is DONE, however will NOT currently work. It has to do with some python
        thing where a class can be loaded twice, and thus have a different ID, and
        super fails a basic "isinstance" test. I BELEIVE this will start working
        once I properly import celery into django, and load celery in a shared
        class space, but I do not want to do that NOW. SO I will continue to use
        the hack tasks until that is done. If this does NOT solve the problem,
        I will either 
        1) Have to give up on this neat trick
        2) Handle super myself?
        3) Read more on http://thingspython.wordpress.com/2010/09/27/another-super-wrinkle-raising-typeerror/
        
        I think it works now...????'''
    from .common_tasks import VipTask, shared_task

    @shared_task(base=VipTask, bind=True)
    def __taskAddSync(self, *args, **kwargs):
      obj = cls(*args, **kwargs)
      obj.service_id = self.request.id
      obj.save()
      return obj.id
    return __taskAddSync.apply(args=args, kwargs=kwargs)

  @classmethod
  def taskAddAsync(cls, *args, **kwargs):
    ''' I do not think this will work, because __taskAdd needs to be registered with
        celery, and it can't be done when it's a inline function, Move to common_tasks, 
        and register. But I won't do that now, until I use taskAddAsync more, and know
        it is working now.'''
#    @shared_task(base=VipTask, bind=True)
    def __taskAddAsync(self, *args, **kwargs):
      obj = cls(*args, **kwargs)
      obj.service_id = self.request.id
      obj.save()
      return obj.id
    return __taskAddAsync.apply_async(args=args, kwargs=kwargs)

  ''' I never finished this. Finish when above is fixed ''' 
  # @classmethod
  # @shared_task(base=VipTask, bind=True)
  # def taskUpdate(self, cls, *args, **kwargs):
    # print self.request.id
    # print cls 
    # print args
    # print kwargs
    
class Session(VipCommonModel):
  '''Model to track everything in a processing session
  
     This is Common Model and not Object model because I expect it to be ever
     changing. The session shall NOT be passed along to celery. Rather, the
     values in the session are USED as the input parameters to a celery task.
     While this may be annoying, it allows us to not need to object track 
     Session while still maintaining out repeatablity and trackability.'''

  origin = models.ForeignKey('CoordinateSystem')
  xRegion =  models.FloatField()
  yRegion =  models.FloatField()
  zRegion =  models.FloatField()
  name = models.CharField(max_length=32)

###  imageCollection = models.ForeignKey('ImageCollection')
#  cameraCollection = models.ForeignKey('CameraCollection')

#class CameraCollection(VipObjectModel):
#  cameras = models.ManyToManyField('Camera')

class Camera(VipObjectModel):
  focalLengthU = models.FloatField()
  focalLengthV = models.FloatField()
  principalPointU = models.FloatField()
  principalPointV = models.FloatField()
  coordinateSystem = models.ForeignKey('CoordinateSystem')
  #Should the camera point to the image instead? Yes!


''' Coordinate systems '''
#this is where the inheritance becomes less good... I worked around it, but still...
class CoordinateSystem(VipObjectModel):
  pass
  #csType = models.CharField(max_length=1, choices=COORDINATE_SYSTEM)
  #srid = models.IntegerField()

class CartesianCoordinateSystem(CoordinateSystem):
  xUnit = models.CharField(max_length=1, choices=LENGTH_UNIT)
  yUnit = models.CharField(max_length=1, choices=LENGTH_UNIT)
  zUnit = models.CharField(max_length=1, choices=LENGTH_UNIT)

class GeoreferenceCoordinateSystem(CoordinateSystem):
  xUnit = models.CharField(max_length=1, choices=LENGTH_UNIT+ANGLE_UNIT)
  yUnit = models.CharField(max_length=1, choices=LENGTH_UNIT+ANGLE_UNIT)
  zUnit = models.CharField(max_length=1, choices=LENGTH_UNIT+ANGLE_UNIT)
  location = models.PointField(dim=3)
  
  def toCartesianCoordinateSystem(self, origin):
    ''' Returns the transformation to go from this Georeference Coordinate
        System to a Cartesian frame At the origin point'''
    pass
  
  objects = InheritanceGeoManager()
  #I need a GeoManager for PostGIS objects

''' Coordinate Transforms '''

class CoordinateTransform(VipObjectModel):
  coordinateSystem_from = models.ForeignKey('CoordinateSystem', related_name='coordinatetransform_from_set')
  coordinateSystem_to   = models.ForeignKey('CoordinateSystem', related_name='coordinatetransform_to_set')
  #I  need to do this for ABSTRACT, but this isn't abstract, so I don't think I need to
  #coordinateSystem_from = models.ForeignKey('CoordinateSystem', related_name='%(app_label)s_%(class)_from_related')
  #coordinateSystem_to   = models.ForeignKey('CoordinateSystem', related_name='%(app_label)s_%(class)_to_related')
  transformType = models.CharField(max_length=1, choices=TRANSFORMATION_TYPE)

class CartesianTransform(CoordinateTransform):
#   rodriguezX = models.FloatField()
#   rodriguezY = models.FloatField()
#   rodriguezZ = models.FloatField()
  rodriguezX = models.PointField(dim=3)
  rodriguezY = models.PointField(dim=3)
  rodriguezZ = models.PointField(dim=3)
  #TOTAL HACK until I get REAL Rodriguez vectors in here, I will Store R!

  translation = models.PointField(dim=3)
  
#  translationX = models.FloatField()
#  translationY = models.FloatField()
#  translationZ = models.FloatField()

''' The rest '''

class ImageCollection(VipObjectModel):
  images = models.ManyToManyField('Image')
  scene = models.ForeignKey('Scene', blank=True, null=True)

class Image(VipObjectModel):
  fileFormat = models.CharField(max_length=4)
  pixelFormat = models.CharField(max_length=1, choices=PIXEL_FORMAT)

  imageWidth = models.PositiveIntegerField('Image Width (pixels)')
  imageHeight = models.PositiveIntegerField('Image Height (pixels)')
  numberColorBands = models.PositiveIntegerField('Number of Color Bands')
  #imageUrl = models.TextField(unique=True)
  #I can't use unique with the current precedence implementation
  imageUrl = models.TextField() #The url for Open Layers
  originalImageUrl = models.TextField() #The url to access original image, untouched. 
  camera = models.ForeignKey('Camera', null=True, blank=True)
  #coordinateSystem = models.ForeignKey('CoordinateSystem', null=True, blank=True)
  #Question for Joe: Point at the camera, or point at the oppisite end of the
  #transformation? 
  original_filename = models.TextField()

  acquisition_date = models.DateTimeField(blank=True, null=True)
  coverage_poly = models.PolygonField(blank=True, null=True)

  class Meta:
    ordering=('name',)
    #Temporary fix, until I get a through class working


class TiePoint(VipObjectModel):
  #description = models.CharField(max_length=250)
  #x = models.FloatField()
  #y = models.FloatField()
  point = models.PointField(dim=2)
  
  image = models.ForeignKey('Image', blank=False)
  geoPoint = models.ForeignKey('ControlPoint', null=True, blank=True)

  objects = InheritanceGeoManager()

class ControlPoint(VipObjectModel):
  description = models.TextField()
  
  point = models.PointField(dim=3, geography=use_geography_points)
  apparentPoint = models.PointField(dim=3, geography=use_geography_points, null=True, blank=True)

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
  filename = models.TextField()
  potree_url = models.TextField() #The url for Potree
  def __str__(self):
    return '%s [%s]' % (self.name, self.origin)
