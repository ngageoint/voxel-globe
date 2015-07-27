from ..common_tasks import app
import voxel_globe.world.models

@app.task(bind=True)
def sleeper(self, seconds):
  import time
  for s in xrange(seconds):
    self.update_state(state='SLEEPING', meta={'t':s, 'total':seconds})
    time.sleep(1);
  return s;

@app.task
def getArea(id):
  from celery.utils.log import get_task_logger
  l = get_task_logger(__name__);
  l.info("Searching for ID %d", id)
  country = voxel_globe.world.models.WorldBorder.objects.get(id=id)
  return country.area;

@app.task(bind=True)
def getAreaLong(self, id):
  ''' This version has status updating.
      Status update available via task.status/task.state and task.result for the meta dictionary'''
  from time import sleep
  from celery.utils.log import get_task_logger
  
  l = get_task_logger(__name__);
  l.info("Long Searching for ID %d", id)
  
  #self.backend.store_result(self.request.id, result={"percent_done": 10}, status="PROGRESS")
  self.update_state(state='PROGRESS', meta={'current': 1, 'total': 3})
  
  l.info("Sleeping 15 seconds")
  sleep(15)
  country = voxel_globe.world.models.WorldBorder.objects.get(id=id)
  l.info("I now know it's %d", country.area)
  l.info("Sleeping another 15 seconds")
  #self.backend.store_result(self.request.id, result={"percent_done": 90}, status="PROGRESS")
  self.update_state(state='PROGRESS', meta={'current': 2, 'total': 3})
  sleep(15)
  self.update_state(state='PROGRESS', meta={'current': 3, 'total': 3})
  return country.area;

@app.task(bind=True)
def printDb(self, id):
  ''' Useful task for probing the boxm2 database of a worker '''
  import boxm2_batch
  from vsi.tools import Redirect, Logger
  from celery.utils.log import get_task_logger
  l = get_task_logger(__name__);
  
  with Redirect(all=Logger(l)):
    l.error(boxm2_batch.print_db())