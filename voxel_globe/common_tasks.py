import sys
from os import environ as env
from functools import partial
from copy import deepcopy


import json

from celery.utils.log import get_task_logger
from celery import Celery, Task, shared_task
from celery.canvas import Signature, chain, group, chunks, xmap, xstarmap, \
                          chord
from celery.signals import task_revoked

import voxel_globe.meta.models

from voxel_globe.websockets import ws_logger


logger = get_task_logger(__name__)


def create_service_instance(inputs="NAY", status="Creating", user=None,
              service_name="NAY", outputs='NAY', **kwargs):
  '''Create new database entry for service instance, and return the entry'''

  service_instance = voxel_globe.meta.models.ServiceInstance(inputs=inputs, 
      status=status, user=user, service_name=service_name, outputs=outputs, 
      **kwargs)
  return service_instance

def vip_unique_id(**kwargs):
  '''Create new database entry for service instance, and return the ID

     This exists to replace celery.util.gen_unique_id'''
  service_instance = create_service_instance(**kwargs)
  service_instance.save()
  return str(service_instance.id)

#Monkey patch
#This patch will go into the celery module responsible for setting the task_id
#(in freeze for Signature)
#for apply, and apply_async and replace the uuid function used. I tried MANY 
#other solutions, and in the end, this the only one I got working. The old 
#solution of redefining apply/apply_async for VipTask did not work for any
#signature related
import celery.canvas
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

#These aren't really tasks right now, so this is not necessary. Use UUID and
#ever thing works. Besides, with this some chord_unlock fails and retries
#infinitely. Something in here must be wrong.

# #This will probably need to be updated in Celery 3.2
# class VipSignatureMixin(object):
#   # def __init__(self, *args, **kwargs):
#   #   kwargs.setdefault('task_id', None)
#   #   if not kwargs['task_id']:
#   #     print '__init__'
#   #     kwargs['task_id'] = vip_unique_id()
#   #   super(VipSignature, self).__init__(*args, **kwargs)
#   def freeze(self, _id=None, group_id=None, chord=None):
#     fid = open('/opt/users/andy/projects/ngap2/vip/logs/celery/wtf.log', 'a')
#     print >>lfid, "Freeze!"
#     print >>fid, _id
#     print >>fid, self.options
#     self.options.setdefault('task_id', _id or vip_unique_id())
#     blah = super(VipSignatureMixin, self).freeze(_id, group_id, chord)
#     print >>fid, self.options
#     return blah

#   def apply_async(self, args=(), kwargs=None, add_to_parent=True, **options):
#     fid = open('/opt/users/andy/projects/ngap2/vip/logs/celery/wtf.log', 'a')
#     print >>fid, "Apply async 2!!?"
#     print >>fid, options
#     print >>fid, self.options
#     #self.options.setdefault('task_id', _id or vip_unique_id())
#     import vsi.tools.vdb_rpdb as vdb
# #    vdb.set_trace()
#     blah = super(VipSignatureMixin, self).apply_async(args, kwargs, add_to_parent, **options)
#     print >>fid, blah
#     print >>fid, self.options
#     return blah

#   def clone(self, args=(), kwargs={}, app=None, **opts):
#     # need to deepcopy options so origins links etc. is not modified.
#     if args or kwargs or opts:
#       args, kwargs, opts = self._merge(args, kwargs, opts)
#     else:
#       args, kwargs, opts = self.args, self.kwargs, self.options
#     s = VipSignature.from_dict({'task': self.task, 'args': tuple(args),
#                                 'kwargs': kwargs, 'options': deepcopy(opts),
#                                 'subtask_type': self.subtask_type,
#                                 'chord_size': self.chord_size,
#                                 'immutable': self.immutable},
#                                 app=app or self._app)
#     s._type = self._type
#     return s


# class VipSignature(VipSignatureMixin, Signature):
#   pass

# @partial(Signature.register_type, name='chain')
# class VipChain(VipSignatureMixin, chain):
#   pass

# @partial(Signature.register_type, name='group')
# class VipGroup(VipSignatureMixin, group):
#   pass

# @partial(Signature.register_type, name='chunks')
# class VipChunks(VipSignature, chunks):
#   pass

# @partial(Signature.register_type, name='chord')
# class VipChord(VipSignature, chord):
#   pass

# @partial(Signature.register_type, name='xmap')
# class VipXmap(VipSignature, xmap):
#   pass

# @partial(Signature.register_type, name='xstarmap')
# class VipXstarmap(VipSignature, xstarmap):
#   pass


class VipTask(Task):
  ''' Create an auto tracking task, aka serviceInstance ''' 
  abstract = True

  def apply_async(self, args=None, kwargs=None, task_id=None, user=None, *args2, **kwargs2):
    '''Automatically create task_id's based off of new primary keys in the
       database. Ignores specified task_id. I decided that was best''' 

    if not task_id:
      print 'apply_async'
      task_id = vip_unique_id(status='Creating Async',
                              inputs=json.dumps((args, kwargs)),
                              user=user,
                              service_name=self.name)
    else:#This only really happens in VIP in a canvas
      service_instance = get_service_instance(task_id)
      service_instance.status='Creating Async'
      service_instance.inputs=json.dumps((args, kwargs))
      service_instance.service_name=self.name
      if user:
        service_instance.user = user
      service_instance.save()

    if 'VIP_CELERY_DBSTOP_ON_START' in env:
      import re
      if re.search(env['VIP_CELERY_DBSTOP_ON_START'], self.name):
        import vsi.tools.vdb_rpdb as vdb
        vdb.set_trace()

    return super(VipTask, self).apply_async(args=args, kwargs=kwargs, 
                                            task_id=task_id, *args2, **kwargs2)

  def apply(self, *args, **kwargs):
    '''Automatically create task_id's based off of new primary keys in the
       database. Ignores specified task_id. I decided that was best''' 
    kwargs.setdefault('task_id', None)
    if not kwargs['task_id']:
      print 'apply'
      kwargs['task_id'] = vip_unique_id(status='Creating Sync',
                                        inputs=json.dumps((args, kwargs)),
                                        service_name=self.name)
    else:
      service_instance = get_service_instance(kwargs['task_id'])
      service_instance.status='Creating Sync'
      service_instance.inputs=json.dumps((args, kwargs))
      service_instance.service_name=self.name
      service_instance.save()

    if 'VIP_CELERY_DBSTOP_ON_START' in env:
      import re
      if re.search(env['VIP_CELERY_DBSTOP_ON_START'], self.name):
        import vsi.tools.vdb_rpdb as vdb
        vdb.set_trace()

    return super(VipTask, self).apply(*args, **kwargs)

  # def subtask(self, args=None, *starargs, **starkwargs):
  #   starkwargs.setdefault('options', {})
  #   starkwargs['options'].setdefault('task_id', None)
  #   if not starkwargs['options']['task_id']:
  #     print 'subtask'
  #     starkwargs['options']['task_id'] = vip_unique_id()
  #   return super(VipTask, self).subtask(args, *starargs, **starkwargs)

  def on_success(self, retval, task_id, args, kwargs):
    #I can't currently tell if apply or apply_async is called, but I don't 
    #think I care either. I could check status since I differentiate them there 

    service_instance = get_service_instance(task_id)

    service_instance.outputs = json.dumps(retval)
    service_instance.status = 'Success'
    service_instance.save()

    ws_logger.send_status_update(task_id=self.request.id, task_name=self.name, 
                                 status="Success", result=retval)

  def on_failure(self, exc, task_id, args, kwargs, einfo):
    if env['VIP_CELERY_DBSTOP_IF_ERROR']=='1':
      import traceback
      import sys
      import vsi.tools.vdb_rpdb as vdb
      import socket

      traceback.print_exception(*sys.exc_info())

      print 'Hostname:', socket.gethostname()
      vdb.post_mortem(ip='0.0.0.0')
    
    service_instance = get_service_instance(task_id)
    service_instance.outputs = json.dumps({"traceback" : str(einfo)})
    service_instance.status = 'Failure'
    service_instance.save()

    ws_logger.send_status_update(task_id=self.request.id, task_name=self.name, 
                                 status="Failure", result={"traceback" : str(einfo)})

  def update_state(self, task_id=None, state=None, meta=None):
    logger.debug('update_state: Task: %s State: %s Meta: %s', task_id, state, 
                 meta)

    service_instance = get_service_instance(self.request.id)
    service_instance.outputs = json.dumps(meta)
    service_instance.status = state
    service_instance.save()

    ws_logger.send_status_update(task_id=self.request.id, task_name=self.name, 
                                 status=state, result=meta)

    return super(VipTask, self).update_state(task_id, state, meta)

#  def on_retry(self, exc, task_id, args, kwargs, einfo):
#    pass

@shared_task
def delete_service_instance(service_id):
  ''' Maintenance routine '''
  service_instance = voxel_globe.meta.models.ServiceInstance.objects.get(
      id=service_id)
  
  sets = filter(lambda x: x.endswith('_set'), dir(service_instance))
  
  for s in sets:
    objects = getattr(service_instance, s).all()
    for obj in objects:
      #parents = getattr(objects, s).all()
      #It will be called the same thing, I hope... The only way this wouldn't
      #be true is if the model definition was REALLY messed up, which shouldn't
      #Be possible with my inheritance schema. So this should always work
      #for parent in parents:
      print 'Dereferencing %s %s %d' % (type(obj), obj.name, obj.id)
      obj.remove_reference()

  print 'Deleting Service Instance tree'
  service_instance.delete()

#TODO
#Define Add task
#--Addes a task, retrieve data from database, etc...
#--Gets a GUID and sets task ID
#--Adds entry for service/taskID into ____ table
