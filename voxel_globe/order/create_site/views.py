from django.shortcuts import render, redirect
from .forms import CreateSiteForm

def make_order(request):
  if request.method == 'POST':
    form = CreateSiteForm(request.POST)

    if form.is_valid():
      name = form.data['name']
      bbox_min = {
        'type': 'Point',
        'coordinates': [
          form.data['south_d'], form.data['west_d'], form.data['bottom_d']
        ]
      }
      bbox_max = {
        'type': 'Point',
        'coordinates': [
          form.data['north_d'], form.data['east_d'], form.data['top_d']
        ]
      }
      print(bbox_max)
      print(bbox_min)

      return redirect('main:index')
  else:
    form = CreateSiteForm()

  return render(request, 'order/create_site/html/make_order.html',
                {'title': 'Voxel Globe - Create Site',
                 'page_title': 'Create Site',
                 'form':form})

def request_task(request, sattel_site_id):
  import urllib2, json, os
  from celery.result import AsyncResult
  from voxel_globe.order.create_site import tasks
  #sattel_site_id = int(request.GET['sattel_site_id'])
  
  task = tasks.create_site.apply_async()
  return redirect('create_site:order_status', task_id=task.id)

def order_status(request, task_id):
  return render(request, 'order/create_site/html/order_status.html',
    {'task_id': task_id})
