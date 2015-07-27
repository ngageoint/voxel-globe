from django.contrib.gis.db import models
from django.core.exceptions import FieldError
from django.db.transaction import atomic;
from django.db.models.fields.related import OneToOneField

from model_utils.managers import InheritanceManager

class InheritanceGeoManager(InheritanceManager, models.GeoManager):
  pass

import json;

from . import history_manager

from uuid import uuid4;

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
                       ('g', 'Geographic'));

MODEL_TYPE = (('vol', 'Volumentric'), ('ph', 'Polyhedral'), ('pl', 'Plane'),
              ('c', 'Cylinder'), ('pc', 'Point Cloud'))

use_geography_points = False

historyManager = history_manager.Histories();

#Temporary code crutch
class History(models.Model):
  name = models.TextField();
  history = models.TextField(); #json field
  
  def __unicode__(self):
    return '%s[%s]' % (self.name, self.id)
  
  @classmethod
  def to_dict(cls, history=None):
    '''Convert a History object, history string, history index or history
       dictionary (idenity case) into a history dictionary'''
    if history is None:
      return None
    elif isinstance(history, dict):
      return history
    elif isinstance(history, str):
      return json.loads(history);
    elif isinstance(history, cls):
      return json.loads(history.history);
    else: #assume it's a number
      return json.loads(cls.objects.get(id=history).history);

class VipCommonModel(models.Model):
  class Meta:
    abstract = True

  objects = InheritanceManager()
  def select_subclasses(self):
    print "BAD BAD BAD! THIS SHOULDN'T BE USED! USE THIS TO KNOW WHAT NEEDS TO BE FIXED!!!"
    print "You should be using more .filter[0] and less .get to get rid of this"
    return self._meta.model.objects.filter(id=self.id).select_subclasses()

  #def get_subclasses(self):
  #  rels = [rel.model.objects.filter(id=self.id) for rel in self._meta.get_all_related_objects()
  #    if isinstance(rel.field, OneToOneField)
  #    and issubclass(rel.field.model, self._meta.model)
  #    and self._meta.model is not rel.field.model]
  #  rels = [rel[0] for rel in rels
  #          if len(rel)]
  #  return rels

  #Returns the string representation of the model. Documentation says I 
  #need to do this. __unicode__ on Python 2
  def __unicode__(self):
    return '%s[%s]' % (self.name, self.id)
  
  def __repr__(self, recurse=0, indent=0):
    s = '';
    for field in self._meta.fields:
      fieldName = field.name;
      try:
        fieldValue = getattr(self, fieldName);
      except: # field.rel.to.DoesNotExist: While this WORKS, I do not understand it, so I will not use it
        fieldValue = "Error: Does Not Exist"
      if isinstance(fieldValue, models.Model):
        if recurse and isinstance(fieldValue, VipCommonModel):
          s += ' '*indent+'%s:\n' % (fieldName)
          s += fieldValue.__repr__(indent=indent+4, recurse=recurse-1);
        else:
          s += ' '*indent+'%s: %s - %s\n' % (fieldName, fieldValue._meta.model_name, unicode(fieldValue))
      else:
        s += ' '*indent+'%s: %s\n' % (fieldName, fieldValue)
        
    for field in self._meta.many_to_many:
      fieldName = field.name;
      s += ' '*indent+'%s\n' % fieldName;
      try:
        fieldValues = getattr(self, fieldName).all();
      except:
        fieldValues = [];
      for m2m in fieldValues:
        if recurse and isinstance(m2m, VipCommonModel):
          s += ' '*(indent+1)+'%s\n' % m2m;
          s += m2m.__repr__(indent=indent+2, recurse=recurse-1);
        else:
          s += ' '*(indent+2)+'%s\n' % m2m;
    return s;

class WorkflowInstance(VipCommonModel):
  name = models.TextField();

class ServiceInstance(VipCommonModel):
  workflow = models.ForeignKey('WorkflowInstance', blank=True, null=True);
  inputs = models.TextField('Inputs');
  outputs = models.TextField('Outputs');
  
  #inputId m2m generic foriegn key
  #outputId m2m generic foriegn key
  
  user = models.CharField(max_length=32);
  entryTime = models.DateTimeField(auto_now_add = True);
  finishTime = models.DateTimeField(auto_now = True); 
  
  status = models.CharField(max_length=32);
  
  serviceName = models.CharField(max_length=128);
  
  def __unicode__(self):
    return '%s [%s]' % (self.serviceName, self.id)

#Abtract common model - GOOD inheritance
class VipObjectModel(VipCommonModel):
  service = models.ForeignKey('ServiceInstance');
  name = models.TextField();
  objectId = models.CharField('Object ID', max_length=36);
  newerVersion = models.ForeignKey('self', null=True, blank=True, related_name='olderVersion');
  deleted = models.BooleanField('Object deleted', default=False);

  class Meta:
    abstract = True

  def getProvenance(self):
    s = ''
    if self.service.workflow:
      s += 'Workflow %s' % (self.service.workflow)

    s += 'Generated by %s\n' % (self.service)
    s += '  Inputs: %s\n' % str(self.service.inputs)
    s += '  Outputs: %s\n' % str(self.service.outputs)

    s += 'Object History (newest first)\n'
    objects = self._meta.model.objects.filter(objectId=self.objectId)
    obj = objects.filter(newerVersion_id=None)[0]
    while 1:
      s += '  %s generated by %s\n' % (obj, obj.service);
      obj = objects.filter(newerVersion_id=obj.id)
      if obj:
        obj=obj[0];
      else:
        break;
    return s;
    
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
    from voxel_globe import tasks

    @tasks.app.task(base=tasks.VipTask, bind=True)
    def __taskAddSync(self, *args, **kwargs):
      obj = cls.create(*args, **kwargs);
      obj.service_id = self.request.id;
      obj.save();
      return obj.id;
    return __taskAddSync.apply(args=args, kwargs=kwargs)

  @classmethod
  def taskAddAsync(cls, *args, **kwargs):
    ''' I do not think this will work, because __taskAdd needs to be registered with
        celery, and it can't be done when it's a inline function, Move to common_tasks, 
        and register. But I won't do that now, until I use taskAddAsync more, and know
        it is working now.'''
#    @tasks.app.task(base=tasks.VipTask, bind=True)
    def __taskAddAsync(self, *args, **kwargs):
      obj = cls.create(*args, **kwargs);
      obj.service_id = self.request.id;
      obj.save();
      return obj.id;
    return __taskAddAsync.apply_async(args=args, kwargs=kwargs)

  ''' I never finished this. Finish when above is fixed ''' 
  # @classmethod
  # @tasks.app.task(base=tasks.VipTask, bind=True)
  # def taskUpdate(self, cls, *args, **kwargs):
    # print self.request.id
    # print cls 
    # print args
    # print kwargs
    
  @classmethod
  def create(cls, *args, **kwargs):
    '''Create an new object, autogenerating a uuid for object ID'''
    obj = cls(*args, **kwargs);
    obj.objectId = str(uuid4());
    return obj;
  
  def _findNewest(self):
    return self._meta.model.objects.get(objectId=self.objectId, newerVersion=None);

  def _findNewest2(self): #The newer filter way, better
    return self._meta.model.objects.filter(objectId=self.objectId, newerVersion=None);
  
  @atomic
  def __update(self, old_id, *args, **kwargs):
    '''Write updates to versioning 
       
       This is the real tricky part, so make it atomic'''

    newest = self._findNewest();
    #print 'newest is', newest
    self.newerVersion_id = None;
    #The most up-to-date is ALWAYS the newest, so it should always be none
    self.save(*args, **kwargs);
    newest.newerVersion_id = self.id;
    newest.save();

    #DON'T DO THIS!!! It may sound like a good idea, but it works when you
    #don't want it to. Every time update is called, the new version will be 
    #added to ever m2m field, and duplicated appear everywhere.
    #Everything is copied EXCEPT m2m, do this separately.
    #Fairly inefficient. I have to load the model instance again if I need it
    #for field in self._meta.get_fields():
    #  old_object = None
    #  m2m = field.is_relation and field.many_to_many
    #  if m2m:
    #    old_object = old_object if old_object is not None \
    #                 else self._meta.model.objects.get(id=old_id)
    #    field_name = field.get_accessor_name()
    #    new_field = getattr(self, field_name)
    #    old_field = getattr(old_object, field_name)
    #    new_field.add(*old_field.all())

  def update(self, _auto_save=True, **kwargs):
    '''Update record and optionally save, turning object into new record

       This will allow you to update any of the fields except m2m fields which
       Must be manually modified, since that is not a simple update.
       
       Automatically saves unless _auto_save is set to False'''

    #Either this is the first update called or subsequent update with 
    #_auto_save=False. So either get the stored or the old id
    old_id = getattr(self, '_update_save', None)
    old_id = old_id if old_id is not None else self.id
    
    #Clear pk and id, which creates a new database entry
    self.pk = None;
    self.id = None;
    #You know, the developer COULD set pk/id, I mean, that would be BAD, but hey, 
    #whatever. I won't prevent it.

    for name, val in kwargs.iteritems():
      field = self._meta.get_field(name)
      #model = field.model._meta.concrete_model
      direct = not field.auto_created or field.concrete
      m2m = field.is_relation and field.many_to_many
      if not direct or m2m:
        raise FieldError('Cannot update model field %r (only non-relations and foreign keys permitted).' % field)
      setattr(self, name, val);

    if _auto_save:
      self.__update(old_id);
    else:
      #save the old id, incase of async save
      setattr(self, '_update_save', old_id);
      

  def save(self, *args, **kwargs):
    '''Save record, and update if internal flag is set, then call built in save'''
    if getattr(self, '_update_save', None) is not None:
      self._update_save = None;
      self.__update(*args, **kwargs);
    else:
      super(VipObjectModel, self).save(*args, **kwargs);
    
  
  def delete(self, using=None, check_is_used=True):
    '''Remove this version of the object ID. 
    
       This function currently does NOT Search all other tables for references, 
       but will in the future. Maybe not.
       
       The check_is_used is a placeholder to skip the check the ServiceInstance
       table to see if this instance is refered to. This is useful to skip if
       there is a global maintanence routine that will have already checked this
       and there is no reason to check here again, for speed.'''

    if check_is_used:
      pass

    self.remove_references(check_is_used);

    super(VipObjectModel, self).delete(using);
    
  def previous_version(self):
    try:
      return getattr(self, self._meta.model_name+'_set').get()
    except self.DoesNotExist:
      return None;
  
  def history(self, history=None, get_subclass=True):
    if history and self.objectId in history:
      hist = self._meta.model.objects.filter(id=history[self.objectId])
    else:
      hist = self._findNewest2();
    
    if get_subclass:
      try:
        return hist.select_subclasses()[0];
      except (TypeError, IndexError):
        pass
    return hist[0];

  @atomic
  def remove_references(self, check_is_used=True):
    ''' This effectively unlinks this node from the history tree so that is can
        later be safely removed '''
    if check_is_used:
      pass; #Not sure what to do here yet
    
    parent = self._meta.model.objects.filter(objectId=self.objectId, newerVersion_id=self.id);

    if parent:
      parent[0].newerVersion_id = self.newerVersion_id;
      parent[0].save();


class Session(VipCommonModel):
  '''Model to track everything in a processing session
  
     This is Common Model and not Object model because I expect it to be ever
     changing. The session shall NOT be passed along to celery. Rather, the
     values in the session are USED as the input parameters to a celery task.
     While this may be annoying, it allows us to not need to object track 
     Session while still maintaining out repeatablity and trackability.'''

  origin = models.ForeignKey('CoordinateSystem')
  xRegion =  models.FloatField();
  yRegion =  models.FloatField();
  zRegion =  models.FloatField();
  name = models.CharField(max_length=32);

###  imageCollection = models.ForeignKey('ImageCollection')
#  cameraCollection = models.ForeignKey('CameraCollection');

#class CameraCollection(VipObjectModel):
#  cameras = models.ManyToManyField('Camera');

class Camera(VipObjectModel):
  focalLengthU = models.FloatField();
  focalLengthV = models.FloatField();
  principalPointU = models.FloatField();
  principalPointV = models.FloatField();
  coordinateSystem = models.ForeignKey('CoordinateSystem')
  #Should the camera point to the image instead? Meaning Camera Collection only
  #and no image Collection... Ask Joe

''' Coordinate systems '''
#this is where the inheritance becomes less good... I worked around it, but still...
class CoordinateSystem(VipObjectModel):
  pass
  #csType = models.CharField(max_length=1, choices=COORDINATE_SYSTEM)
  #srid = models.IntegerField();

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
    pass;
  
  objects = InheritanceGeoManager()
  #I need a GeoManager for PostGIS onjects

''' Coordinate Transforms '''

class CoordinateTransform(VipObjectModel):
  coordinateSystem_from = models.ForeignKey('CoordinateSystem', related_name='coordinatetransform_from_set')
  coordinateSystem_to   = models.ForeignKey('CoordinateSystem', related_name='coordinatetransform_to_set')
  #I  need to do this for ABSTRACT, but this isn't abstract, so I don't think I need to
  #coordinateSystem_from = models.ForeignKey('CoordinateSystem', related_name='%(app_label)s_%(class)_from_related')
  #coordinateSystem_to   = models.ForeignKey('CoordinateSystem', related_name='%(app_label)s_%(class)_to_related')
  transformType = models.CharField(max_length=1, choices=TRANSFORMATION_TYPE)

class CartesianTransform(CoordinateTransform):
#   rodriguezX = models.FloatField();
#   rodriguezY = models.FloatField();
#   rodriguezZ = models.FloatField();
  rodriguezX = models.PointField(dim=3);
  rodriguezY = models.PointField(dim=3);
  rodriguezZ = models.PointField(dim=3);
  #TOTAL HACK until I get REAL Rodriguez vectors in here, I will Store R!

  translation = models.PointField(dim=3);
  
#  translationX = models.FloatField();
#  translationY = models.FloatField();
#  translationZ = models.FloatField();

''' The rest '''

class VipManyToManyField(models.ManyToManyField):
  def history(self, history=None):
    pass
    #return querySet with the history version?

class ImageCollection(VipObjectModel):
  images = VipManyToManyField('Image');

class Image(VipObjectModel):
  fileFormat = models.CharField(max_length=4);
  pixelFormat = models.CharField(max_length=1, choices=PIXEL_FORMAT);

  imageWidth = models.PositiveIntegerField('Image Width (pixels)');
  imageHeight = models.PositiveIntegerField('Image Height (pixels)');
  numberColorBands = models.PositiveIntegerField('Number of Color Bands');
  #imageUrl = models.TextField(unique=True);
  #I can't use unique with the current precedence implementation
  imageUrl = models.TextField(); #The url for Open Layers
  originalImageUrl = models.TextField(); #The url to access original image, untouched. 
  camera = models.ForeignKey('Camera', null=True, blank=True);
  #coordinateSystem = models.ForeignKey('CoordinateSystem', null=True, blank=True);
  #Question for Joe: Point at the camera, or point at the oppisite end of the
  #transformation? 
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

  #latitude = models.FloatField()
  #longitude = models.FloatField()
  #altitude = models.FloatField()
    
  #apparentLatitude = models.FloatField()
  #apparentLongitude = models.FloatField()
  #apparentAltitude = models.FloatField()

class Scene(VipObjectModel):
  origin = models.PointField(dim=3, null=False, blank=False)
  geolocated = models.BooleanField(default=True) #REFACT: Remove the default, make required
  bbox_min = models.PointField(dim=3, default='POINT(0 0 0)')#REFACT: , null=False, blank=False)
  bbox_max = models.PointField(dim=3, default='POINT(0 0 0)')#REFACT: , null=False, blank=False)
  default_voxel_size = models.PointField(dim=3, default='POINT(0 0 0)')#REFACT: , null=False, blank=False)
  
  def __unicode__(self):
    return '%s [%s]' % (self.name, self.origin)

class VoxelWorld(VipObjectModel):
  origin = models.PointField(dim=3, geography=use_geography_points, null=False, blank=False)
  voxel_world_dir = models.TextField();
  def __unicode__(self):
    return '%s [%s]' % (self.name, self.origin)
