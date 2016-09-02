from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

def make_order_1(request):
  from voxel_globe.meta import models
  voxel_world_list = models.VoxelWorld.objects.all()
  return render(request, 'order/threshold_point_cloud/html/make_order_1.html', 
                {'voxel_world_list':voxel_world_list})

def make_order_2(request, voxel_world_id):
  return  render(request, 'order/threshold_point_cloud/html/make_order_2.html',
                 {'voxel_world_id':voxel_world_id})

def make_order_3(request, voxel_world_id):
  from voxel_globe.generate_point_cloud import tasks

  voxel_world_id = int(voxel_world_id)
  threshold = float(request.POST['threshold'])

  t = tasks.generate_threshold_point_cloud.apply_async(args=(voxel_world_id, 
      threshold), user=request.user)
  
  return render(request, 'order/threshold_point_cloud/html/make_order_3.html',
                {'task_id': t.task_id})
  
def order_status(request):
  pass