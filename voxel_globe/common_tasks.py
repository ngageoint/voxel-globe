###import boxm2_smart_register
#This need to me imported before other boxm2 because of how it's designed

import json

import voxel_globe.meta.models

from celery import Celery, Task, group

from os import environ as env

app = Celery(env['VIP_CELERY_APP']);
app.config_from_object(env['VIP_CELERY_CONFIG_MODULE']) #Don't need this because celeryd does it for me?

class VipTask(Task):
  ''' Create an auto tracking task, aka serviceInstance ''' 
  abstract = True
  
  def __createServiceIntanceEntry(self, inputs=None, user="NAY"):
    '''Create initial database entry for service instance, and return the ID'''
    
    serviceInstance = voxel_globe.meta.models.ServiceInstance(
                          inputs=json.dumps(inputs),
                          status="Creating",
                          user=user,
                          serviceName=self.name, #Next TODO
                          outputs='NAY');
    serviceInstance.save();
    return str(serviceInstance.id);
    
  def __updateServiceIntanceEntry(self, output, task_id, status,
                                        args=None, kwargs=None):
    try:
      serviceInstance = voxel_globe.meta.models.ServiceInstance.objects.get(id=task_id);
      #serviceInstance = voxel_globe.meta.models.ServiceInstance.objects.get_for_id(task_id);
    except voxel_globe.meta.models.ServiceInstance.DoesNotExist:
      #Else it's just missing, create it
      status="Impromptu:"+status;
      task_id = self.__createServiceIntanceEntry((args, kwargs));
      serviceInstance = voxel_globe.meta.models.ServiceInstance.objects.get(id=task_id);

    serviceInstance.outputs = json.dumps(output)
    serviceInstance.status = status;
    serviceInstance.save();

  def apply_async(self, args=None, kwargs=None, task_id=None, *args2, **kwargs2):
    '''Automatically create task_id's based off of new primary keys in the
       database. Ignores specified task_id. I decided that was best''' 
    taskID = self.__createServiceIntanceEntry((args, kwargs));
    
    return super(VipTask, self).apply_async(args=args, kwargs=kwargs, 
                                            task_id=taskID, *args2, **kwargs2)
  
  def apply(self, args=None, kwargs=None, *args2, **kwargs2):
    '''Automatically create task_id's based off of new primary keys in the
       database. Ignores specified task_id. I decided that was best''' 
    if kwargs:
      kwargs.pop('task_id', None); #Remove task_id incase it is specified.
      #apply is different from apply_async in this manner

    taskID = self.__createServiceIntanceEntry((args, kwargs));

    return super(VipTask, self).apply(args=args, kwargs=kwargs, task_id=taskID,
                                      *args2, **kwargs2)
  
#  def after_return(self, status, retval, task_id, args, kwargs, einfo): #, *args2, **kwargs2
  def on_success(self, retval, task_id, args, kwargs):
    #I can't currently tell if apply or apply_asyn is called, but I don't think I care
    self.__updateServiceIntanceEntry(retval, task_id, 'Success', args, kwargs);
  
  def on_failure(self, exc, task_id, args, kwargs, einfo):
    if env['VIP_CELERY_DBSTOP_IF_ERROR']=='1':
      import traceback
      import sys
      import vsi.tools.vdb_rpdb as vdb

      traceback.print_exception(*sys.exc_info())
      vdb.post_mortem()
    self.__updateServiceIntanceEntry(str(einfo), task_id, 'Failure',
                                     args, kwargs);
    
#  def on_retry(self, exc, task_id, args, kwargs, einfo):
#    pass

@app.task
def deleteServiceInstance(service_id):
  ''' Maintanence routine '''
  serviceInstance = voxel_globe.meta.models.ServiceInstance.objects.get(id=service_id);
  
  sets = filter(lambda x: x.endswith('_set'), dir(serviceInstance))
  
  for s in sets:
    objects = getattr(serviceInstance, s).all();
    for obj in objects:
      #parents = getattr(objects, s).all();
      #It will be called the same thing, I hope... The only way this wouldn't
      #be true is if the model definition was REALLY messed up, which shouldn't
      #Be possible with my inheritance schema. So this should always work
      #for parent in parents:
      print 'Dereferencing %s %s %d' % (type(obj), obj.name, obj.id)
      obj.remove_reference();

  print 'Deleting Service Instance tree'
  serviceInstance.delete();



#TODO
#Define Add task
#--Addes a task, retrieve data from database, etc...
#--Gets a GUID and sets task ID
#--Adds entry for service/taskID into ____ table

#Workflows?
#Need to read up on Celery to see if it already does workflows

'''
Avoid launching synchronous subtasks

Having a task wait for the result of another task is really inefficient, and may even cause a deadlock if the worker pool is exhausted.

Make your design asynchronous instead, for example by using callbacks.

Bad:

@app.task
def update_page_info(url):
    page = fetch_page.delay(url).get()
    info = parse_page.delay(url, page).get()
    store_page_info.delay(url, info)

@app.task
def fetch_page(url):
    return myhttplib.get(url)

@app.task
def parse_page(url, page):
    return myparser.parse_document(page)

@app.task
def store_page_info(url, info):
    return PageInfo.objects.create(url, info)

Good:

def update_page_info(url):
    # fetch_page -> parse_page -> store_page
    chain = fetch_page.s() | parse_page.s() | store_page_info.s(url)
    chain()

@app.task()
def fetch_page(url):
    return myhttplib.get(url)

@app.task()
def parse_page(page):
    return myparser.parse_document(page)

@app.task(ignore_result=True)
def store_page_info(info, url):
    PageInfo.objects.create(url=url, info=info)

Here I instead created a chain of tasks by linking together different subtask()'s. You can read about chains and other powerful constructs at Canvas: Designing Workflows.'''
