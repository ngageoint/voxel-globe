from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from voxel_globe.tools import session

cookie_name = 'voxel_globe_order_tiepoint_error_calculation_session'

@session.StartSession(cookie=cookie_name)
def make_order_1(request):
  from voxel_globe.meta import models
  image_set_list = models.ImageSet.objects.all()
  return render(request, 'order/tiepoint_error_calculation/html/make_order_1.html', 
                {'image_set_list':image_set_list})

@session.CheckSession(cookie=cookie_name)
def make_order_2(request, image_set_id):
  from voxel_globe.meta import models
  scene_list = models.Scene.objects.all()
  return render(request, 'order/tiepoint_error_calculation/html/make_order_2.html',
                {'scene_list':scene_list,
                 'image_set_id':image_set_id})

@session.EndSession(cookie=cookie_name)
def make_order_3(request, image_set_id, scene_id):
  from voxel_globe.tiepoint_registration import tasks

  image_set_id = int(image_set_id)
  
  t = tasks.tiepoint_error_calculation.apply_async(args=(image_set_id, scene_id))
  
  return render(request, 'order/tiepoint_error_calculation/html/make_order_3.html',
                {'task_id': t.task_id})
  
def order_status(request, task_id):
  from celery.result import AsyncResult
  
  task = AsyncResult(task_id)

  return render(request, 'task/html/task_3d_error_results.html',
                {'task': task})
