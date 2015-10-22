import django.conf
import importlib

from voxel_globe.vip.celery import app

class IngestClass(object):
  def __init__(self, ingest_data, description=''):
    self.ingest=ingest_data
    self.description=description

#key: [Friendly name, moduleName]
#Module name should not include tasks, but it is assume that tasks.ingest_data is used
#I'm sure this will be updated at a later time to have api data in the module rather than here 
#SENSOR_TYPES = {'arducopter':'Arducopter', 
#                'jpg_exif':'JPEG with EXIF tags'};
#to be used in conjunction with importlib

def preload_tasks():
  ''' Load up app.tasks

      app.tasks isn't populated until all the .tasks modules are loaded. Short
      of finding the RIGHT way to load all the tasks specified in Django, I 
      just load them all myself here.

      I APPARENTLY shouldn't be doing this... Investigate new registry method
      Maybe ONLY load voxel_globe.ingest.*.tasks??? I wouldn't mind that much'''
  for tasks in django.conf.settings.INSTALLED_APPS:
    try:
      importlib.import_module(tasks+'.tasks')
    except (ImportError):
      pass

def get_ingest_types():
  ''' Helper function to get all registered ingest functions '''
  preload_tasks()
  payloads = {}
  metadatas = {}
  for _, task in app.tasks.iteritems():
    try:
      if task.payload_ingest:
        payloads[task.dbname] = IngestClass(task, task.description)
    except AttributeError:
      pass
    try:
      if task.metadata_ingest:
        metadatas[task.dbname] = IngestClass(task, task.description)
    except AttributeError:
      pass

  return payloads, metadatas
PAYLOAD_TYPES, METADATA_TYPES = get_ingest_types()
#PAYLOAD_TYPES = app.tasks
