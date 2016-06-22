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
