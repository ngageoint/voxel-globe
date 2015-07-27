from django.shortcuts import render
from django.http import HttpResponse

from ...meta import models
from ...meta.tools import getHistory
from uuid import uuid4

from .models import Session

# Create your views here.
def make_order_1(request):
  #Choose the image collection

  uuid = uuid4();
  session = Session(uuid=uuid, owner=request.user);
  session.save();

  image_collection_list = models.ImageCollection.objects.all();
  response = render(request, 'order/visualsfm/html/make_order_1.html', 
                {'image_collection_list':image_collection_list});
  response.set_cookie('order_visualsfm', uuid, max_age=15*60)
  return response;

def make_order_2(request, image_collection_id):
  #Choose the scene
  scene_list = models.Scene.objects.all()
  
  return render(request, 'order/visualsfm/html/make_order_2.html',
                {'scene_list':scene_list,
                 'image_collection_id':image_collection_id})

def make_order_3(request, image_collection_id, scene_id):
  #MAKE the actual ORDER!
  from ...visualsfm import tasks
  
  try:
    uuid = request.COOKIES['order_visualsfm'];
    session = Session.objects.get(uuid=uuid);
    session.delete();
  except:
    response = HttpResponse('Session Expired')
    try:
      response.delete_cookie('order_visualsfm')
    finally:
      return response;

  history = getHistory(request.REQUEST.get('history', None))

  t = tasks.runVisualSfm.apply_async(args=(image_collection_id, scene_id, True, history))

  #Crap ui filler   
  image_collection = models.ImageCollection.objects.get(id=image_collection_id);
  image_list = image_collection.images;
  #WARNING, Source of History error, but images shouldn't change!?
  scene = models.Scene.objects.get(id=scene_id);
  
  #CALL THE CELERY TASK!
  response = render(request, 'order/visualsfm/html/make_order_3.html', 
                   {'origin':scene.origin,
                    'image_list':image_list, 'task_id':t.task_id})
  response.delete_cookie('order_visualsfm')
  
  return response
  
def order_status(request, task_id):
  import urllib2, json, os
  from celery.result import AsyncResult
  
  task = AsyncResult(task_id);
  
  #u = urllib2.urlopen('http://%s:%s/api/task/info/%s' % (os.environ['VIP_FLOWER_HOST'], 
  #                                                       os.environ['VIP_FLOWER_PORT'], 
  #                                                       task_id))
  
  #status = json.loads(u.read());
  #status['task_id'] = status['task-id']
  #jinja2 limitation
  
  status = {'task': task};
  
  if task.state == 'PROCESSING' and task.result['stage'] == 'generate match points':
    from vsi.iglob import glob
    status['mat'] = len(glob(os.path.join(task.result['processing_dir'], '*.mat'), False))
    status['sift'] = len(glob(os.path.join(task.result['processing_dir'], '*.sift'), False))
  
  return render(request, 'order/visualsfm/html/order_status.html',
                status)
  #return HttpResponse('Task %s\n%s' % (task_id, status))
