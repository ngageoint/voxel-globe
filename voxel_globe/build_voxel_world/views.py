from django.shortcuts import render, redirect
from django.http import HttpResponse

from uuid import uuid4

from voxel_globe.meta import models

from .forms import OrderVoxelWorldBaseForm, OrderVoxelWorldDegreeForm, OrderVoxelWorldMeterForm, OrderVoxelWorldUnitForm

def make_order(request):
  if request.method == 'POST':
    form_base   = OrderVoxelWorldBaseForm(request.POST)
    form_degree = OrderVoxelWorldDegreeForm(request.POST)
    form_meter  = OrderVoxelWorldMeterForm(request.POST)
    form_unit   = OrderVoxelWorldUnitForm(request.POST)

    if form_base.is_valid() and form_meter.is_valid():
      from voxel_globe.build_voxel_world import tasks
      #voxel_world_id = form.data['voxel_world']
      #mean_multiplier = form.cleaned_data['number_means']
      image_set_id = form_base.data['image_set']
      camera_set_id = form_base.data['camera_set']
      scene = models.Scene.objects.get(id=form_base.data['scene'])

      bbox = {'x_min': form_meter.cleaned_data['west_m'], 
              'y_min': form_meter.cleaned_data['south_m'], 
              'z_min': form_meter.cleaned_data['bottom_m'], 
              'x_max': form_meter.cleaned_data['east_m'], 
              'y_max': form_meter.cleaned_data['north_m'], 
              'z_max': form_meter.cleaned_data['top_m'],
              'voxel_size': form_meter.cleaned_data['voxel_size_m'],
              'geolocated': scene.geolocated}

      skipFrames = 1

      if form_base.cleaned_data['regularization']:
        task = tasks.run_build_voxel_model_bp.apply_async(args=(image_set_id, 
            camera_set_id, scene.id, bbox, skipFrames, True), 
            user=request.user)
      else:
        task = tasks.run_build_voxel_model.apply_async(args=(image_set_id, 
            camera_set_id, scene.id, bbox, skipFrames, True), 
            user=request.user)
      auto_open = True

      # import voxel_globe.filter_number_observations.tasks as tasks
      # task = tasks.filter_number_observations.apply_async(args=(voxel_world_id,mean_multiplier))

    if form_base.is_valid() and form_unit.is_valid():
      from voxel_globe.build_voxel_world import tasks
      
      image_set_id = form_base.data['image_set']
      camera_set_id = form_base.data['camera_set']
      scene = models.Scene.objects.get(id=form_base.data['scene'])

      bbox = {'x_min': form_unit.cleaned_data['west_u'], 
              'y_min': form_unit.cleaned_data['south_u'], 
              'z_min': form_unit.cleaned_data['bottom_u'], 
              'x_max': form_unit.cleaned_data['east_u'], 
              'y_max': form_unit.cleaned_data['north_u'], 
              'z_max': form_unit.cleaned_data['top_u'],
              'voxel_size': form_unit.cleaned_data['voxel_size_u'],
              'geolocated': scene.geolocated}

      skipFrames = 1
      if form_base.cleaned_data['regularization']:
        task = tasks.run_build_voxel_model_bp.apply_async(args=(image_set_id, 
            camera_set_id, scene.id, bbox, skipFrames, True), 
            user=request.user)
      else:
        task = tasks.run_build_voxel_model.apply_async(args=(image_set_id, 
            camera_set_id, scene.id, bbox, skipFrames, True), 
            user=request.user)
      auto_open = True

  else:
    auto_open = False
    form_base   = OrderVoxelWorldBaseForm()
    form_degree = OrderVoxelWorldDegreeForm()
    form_meter  = OrderVoxelWorldMeterForm()
    form_unit   = OrderVoxelWorldUnitForm()

  return render(request, 'build_voxel_world/html/make_order.html',
                {'title': 'Voxel Globe - Build Voxel World',
                 'page_title': 'Build Voxel World',
                 'form_base':form_base, 'form_degree':form_degree,
                 'form_meter':form_meter, 'form_unit':form_unit,
                 'task_menu_auto_open': auto_open})

def order_status(request, task_id):
  import urllib2, json, os
  from celery.result import AsyncResult
  
  task = AsyncResult(task_id)
  
  status = {'task': task}
 
  return render(request, 'build_voxel_world/html/order_status.html',
                status)
  #return HttpResponse('Task %s\n%s' % (task_id, status))
