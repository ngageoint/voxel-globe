from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from voxel_globe.tools import session

cookie_name = 'voxel_globe_order_tiepoint_error_calculation_session'

@session.StartSession(cookie=cookie_name)
def make_order_1(request):
  from voxel_globe.meta import models
  image_collection_list = models.ImageCollection.objects.all();
  return render(request, 'order/tiepoint_error_calculation/html/make_order_1.html', 
                {'image_collection_list':image_collection_list});

@session.CheckSession(cookie=cookie_name)
def make_order_2(request, image_collection_id):
  from voxel_globe.meta import models
  scene_list = models.Scene.objects.all()
  return render(request, 'order/tiepoint_error_calculation/html/make_order_2.html',
                {'scene_list':scene_list,
                 'image_collection_id':image_collection_id})

@session.EndSession(cookie=cookie_name)
def make_order_3(request, image_collection_id, scene_id):
  from voxel_globe.tiepoint_registration import tasks
  from voxel_globe.meta.tools import getHistory

  image_collection_id = int(image_collection_id)
  history = getHistory(request.REQUEST.get('history', None))
  
  t = tasks.tiepoint_error_calculation.apply_async(args=(image_collection_id, scene_id),
                                                   kwargs={'history': history})
  
  return render(request, 'order/tiepoint_error_calculation/html/make_order_3.html',
                {'task_id': t.task_id})
  
def order_status(request, task_id):
  from celery.result import AsyncResult
  
  task = AsyncResult(task_id)

  return render(request, 'task/html/task_3d_error_results.html',
                {'task': task})
