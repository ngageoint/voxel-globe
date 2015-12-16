from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

def make_order_1(request):
  from voxel_globe.meta import models
  voxel_world_list = models.VoxelWorld.objects.all();
  response = render(request, 'order/point_cloud/html/make_order_1.html', 
                    {'voxel_world_list':voxel_world_list});
  return response

def make_order_2(request, voxel_world_id):
  from voxel_globe.generate_point_cloud import tasks
  from voxel_globe.meta.tools import getHistory

  request_data = request.POST
  voxel_world_id = int(voxel_world_id)

  history = getHistory(request.REQUEST.get('history', None))
  
  t = tasks.generate_point_cloud.apply_async(args=(voxel_world_id, ),
                                             kwargs={'history': history})
  
  response = render(request, 'order/point_cloud/html/make_order_2.html',
                    {'task_id': t.task_id})
  return response

def order_status(request):
  pass