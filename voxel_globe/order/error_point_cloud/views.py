from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from .forms import ErrorPointCloudOrderForm

def make_order(request):
  if request.method == 'POST':

    form = ErrorPointCloudOrderForm(request.POST)

    if form.is_valid():
      from voxel_globe.generate_point_cloud import tasks

      #task = tasks.create_height_map.apply_async(
      #    args=(form.data['voxel_world'],form.cleaned_data['render_height']))

      task = tasks.generate_error_point_cloud.apply_async(
          args=(form.data['voxel_world'], form.cleaned_data['threshold'],
                form.cleaned_data['position_error'], 
                form.cleaned_data['orientation_error']),
          user=request.user)
      auto_open = True

      # return render(request, 'task/html/task_started.html',
      #               {'title': 'Voxel Globe - Error Point Cloud Ordered',
      #                'page_title': 'Error Point Cloud Ordered',
      #                'task_id':task.id})

  else:
    form = ErrorPointCloudOrderForm()
    auto_open = False

  return render(request, 'order/error_point_cloud/html/make_order.html',
                {'form':form,
                 'task_menu_auto_open': auto_open})


def make_order_1(request):
  from voxel_globe.meta import models
  voxel_world_list = models.VoxelWorld.objects.all()
  return render(request, 'order/error_point_cloud/html/make_order_1.html', 
                {'voxel_world_list':voxel_world_list})

def make_order_2(request, voxel_world_id):
  return  render(request, 'order/error_point_cloud/html/make_order_2.html',
                 {'voxel_world_id':voxel_world_id})

def make_order_3(request, voxel_world_id):
  from voxel_globe.generate_point_cloud import tasks

  voxel_world_id = int(voxel_world_id)
  threshold = float(request.POST['threshold'])

  t = tasks.generate_error_point_cloud.apply_async(args=(voxel_world_id, threshold),
                                                   user=request.user)
  
  return render(request, 'order/error_point_cloud/html/make_order_3.html',
                {'task_id': t.task_id})
  
def order_status(request):
  pass