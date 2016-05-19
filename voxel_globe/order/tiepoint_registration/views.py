from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from voxel_globe.tools import session

cookie_name = 'voxel_globe_order_tiepoint_registration'

@session.StartSession(cookie=cookie_name)
def make_order_1(request):
  from voxel_globe.meta import models
  image_set_list = models.ImageSet.objects.all()
  return render(request, 'order/tiepoint_registration/html/make_order_1.html', 
                {'image_set_list':image_set_list})

@session.EndSession(cookie=cookie_name)
def make_order_2(request, image_set_id):
  from voxel_globe.tiepoint_registration import tasks

  image_set_id = int(image_set_id)
  
  t = tasks.tiepoint_registration.apply_async(args=(image_set_id,))
  
  return render(request, 'order/tiepoint_registration/html/make_order_2.html',
                {'task_id': t.task_id})
  