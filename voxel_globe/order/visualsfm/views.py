from django.shortcuts import render
from django.http import HttpResponse

from voxel_globe.meta import models
from uuid import uuid4

from .models import Session

# Create your views here.
def make_order_1(request):
  #Choose the image set

  uuid = uuid4()
  session = Session(uuid=uuid, owner=request.user)
  session.save()

  image_set_list = models.ImageSet.objects.all()
  response = render(request, 'order/visualsfm/html/make_order_1.html', 
                {'image_set_list':image_set_list})
  response.set_cookie('order_visualsfm', uuid, max_age=15*60)
  return response

def make_order_2(request, image_set_id):
  #Choose the scene
  scene_list = models.Scene.objects.all()
  
  return render(request, 'order/visualsfm/html/make_order_2.html',
                {'scene_list':scene_list,
                 'image_set_id':image_set_id})

def make_order_3(request, image_set_id, scene_id):
  #MAKE the actual ORDER!
  from voxel_globe.visualsfm import tasks
  
  try:
    uuid = request.COOKIES['order_visualsfm']
    session = Session.objects.get(uuid=uuid)
    session.delete()
  except:
    response = HttpResponse('Session Expired')
    try:
      response.delete_cookie('order_visualsfm')
    finally:
      return response

  t = tasks.runVisualSfm.apply_async(args=(image_set_id, scene_id, True))

  #Crap ui filler   
  image_set = models.ImageSet.objects.get(id=image_set_id)
  image_list = image_set.images
  scene = models.Scene.objects.get(id=scene_id)
  
  #CALL THE CELERY TASK!
  response = render(request, 'order/visualsfm/html/make_order_3.html', 
                   {'origin':scene.origin,
                    'image_list':image_list, 'task_id':t.task_id})
  response.delete_cookie('order_visualsfm')
  
  return response
  
def order_status(request, task_id):
  import urllib2, json, os
  from celery.result import AsyncResult
  
  task = AsyncResult(task_id)
  
  #u = urllib2.urlopen('http://%s:%s/api/task/info/%s' % (os.environ['VIP_FLOWER_HOST'], 
  #                                                       os.environ['VIP_FLOWER_PORT'], 
  #                                                       task_id))
  
  #status = json.loads(u.read())
  #status['task_id'] = status['task-id']
  #jinja2 limitation
  
  status = {'task': task}
  
  if task.state == 'PROCESSING' and task.result['stage'] == 'generate match points':
    from vsi.iglob import glob
    status['mat'] = len(glob(os.path.join(task.result['processing_dir'], '*.mat'), False))
    status['sift'] = len(glob(os.path.join(task.result['processing_dir'], '*.sift'), False))
  
  return render(request, 'order/visualsfm/html/order_status.html',
                status)
  #return HttpResponse('Task %s\n%s' % (task_id, status))
