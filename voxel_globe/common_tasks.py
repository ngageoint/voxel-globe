import json

import voxel_globe.meta.models

import sys

from celery import Celery, Task, group, shared_task
from celery.canvas import Signature, chain

from os import environ as env

def create_service_instance():
  '''Create new database entry for service instance, and return the entry'''
  service_instance = voxel_globe.meta.models.ServiceInstance(
      inputs="NAY", status="Creating", user="NAY", serviceName="NAY",
      outputs='NAY');
  return service_instance

def vip_unique_id():
  '''Create new database entry for service instance, and return the ID

     This exists to replace celery.util.gen_unique_id'''
  service_instance = create_service_instance()
  service_instance.save()
  return str(service_instance.id)

#Monkey patch
#This patch will go into the celery modules responsible for setting the task_id
#for apply, and apply_async and replace the uuid function used. I tried MANY 
#other solutions, and in the end, this the only one I got working. The old 
#solution of redefining apply/apply_async for VipTask did not work for any
#signature related
import celery.app.task
import celery.app.base
import celery.canvas
celery.app.task.uuid = vip_unique_id
celery.app.base.uuid = vip_unique_id
celery.canvas.uuid = vip_unique_id

def get_service_instance(service_id):
  '''Get service instance by id, if it doesn't exist, create a new one

     Does not save if a new service instance is created. It is expected that
     this kind of behavior is only useful if you plan on updating and saving'''

  try:
    service_instance = voxel_globe.meta.models.ServiceInstance.objects.get(
        id=int(service_id))
  except voxel_globe.meta.models.ServiceInstance.DoesNotExist:
    #Else it's just missing, create it
    service_instance = create_service_instance()

  return service_instance

def update_service_intance_entry(output, task_id, status,
                                 args=None, kwargs=None):
    service_instance = get_service_instance(task_id)

    service_instance.outputs = json.dumps(output)
    service_instance.status = status;
    service_instance.save();


class VipTask(Task):
  ''' Create an auto tracking task, aka serviceInstance ''' 
  abstract = True
  
  def on_success(self, retval, task_id, args, kwargs):
    #I can't currently tell if apply or apply_asyn is called, but I don't think I care
    update_service_intance_entry(retval, task_id, 'Success', args, kwargs);
  
  def on_failure(self, exc, task_id, args, kwargs, einfo):
    if env['VIP_CELERY_DBSTOP_IF_ERROR']=='1':
      import traceback
      import sys
      import vsi.tools.vdb_rpdb as vdb

      traceback.print_exception(*sys.exc_info())
      vdb.post_mortem()
    update_service_intance_entry
    update_service_intance_entry(str(einfo), task_id, 'Failure',
                                 args, kwargs);
    
#  def on_retry(self, exc, task_id, args, kwargs, einfo):
#    pass

@shared_task
def delete_service_instance(service_id):
  ''' Maintenance routine '''
  service_instance = voxel_globe.meta.models.ServiceInstance.objects.get(
      id=service_id);
  
  sets = filter(lambda x: x.endswith('_set'), dir(service_instance))
  
  for s in sets:
    objects = getattr(service_instance, s).all();
    for obj in objects:
      #parents = getattr(objects, s).all();
      #It will be called the same thing, I hope... The only way this wouldn't
      #be true is if the model definition was REALLY messed up, which shouldn't
      #Be possible with my inheritance schema. So this should always work
      #for parent in parents:
      print 'Dereferencing %s %s %d' % (type(obj), obj.name, obj.id)
      obj.remove_reference();

  print 'Deleting Service Instance tree'
  service_instance.delete();



#TODO
#Define Add task
#--Addes a task, retrieve data from database, etc...
#--Gets a GUID and sets task ID
#--Adds entry for service/taskID into ____ table
