from django.shortcuts import render, redirect
from .forms import CreateSiteForm

def make_order(request):
  if request.method == 'POST':
    from voxel_globe.order.create_site import tasks
    sattel_site_id = int(request.POST.get('sattel_site_id', -1))
    task = tasks.create_site.apply_async(args=([sattel_site_id]))
    return redirect('create_site:order_status', task_id=task.id)

  else:
    form = CreateSiteForm()
    return render(request, 'order/create_site/html/make_order.html',
                  {'title': 'Voxel Globe - Create Site',
                   'page_title': 'Create Site',
                   'form':form})

def order_status(request, task_id):
  import urllib2, json, os
  from celery.result import AsyncResult
  task = AsyncResult(task_id)
  status = {'task': task}
  return render(request, 'order/create_site/html/order_status.html', status)

def image_view(request):
  if request.method == 'POST':
    pass
  else:
    return render(request, 'order/create_site/html/image_view.html',
                  {'title': 'Voxel Globe - Image View',
                  'page_title': 'Image View'})

def temp(request):
  if request.method == 'POST':
    pass
  else:
    return render(request, 'order/create_site/html/temp.html',
                  {'title': 'Voxel Globe - Event Detection',
                  'page_title': 'Event Detection'})