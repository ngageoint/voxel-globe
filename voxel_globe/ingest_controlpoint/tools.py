import django.conf
import importlib

from voxel_globe.vip.celery import app

from voxel_globe.ingest.tools import IngestClass, preload_tasks

def get_ingest_types():
  ''' Helper function to get all registered ingest functions '''
  preload_tasks()
  controlpoints = {}
  for _, task in app.tasks.iteritems():
    try:
      if task.controlpoint_ingest:
        controlpoints[task.dbname] = IngestClass(task, task.description)
    except AttributeError:
      pass

  return controlpoints

CONTROLPOINT_TYPES = get_ingest_types()
