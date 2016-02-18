from django.shortcuts import render, redirect
# Create your views here. Mostly placeholders

from .forms import HeightProcessForm

def make_order(request):
  if request.method == 'POST':

    form = HeightProcessForm(request.POST)

    if form.is_valid():
      import voxel_globe.height_map.tasks as tasks

      image_id = form.data['image']

      task = tasks.height_map_error.apply_async(args=(image_id,))

      return redirect('dem_error:order_status', task_id=task.id)
      #return render(request, 'task/html/task_started.html',
      #              {'title': 'Voxel Globe - DEM Error Calculation',
      #               'page_title': 'Voxel Globe - DEM Error Calculation',
      #               'task_id':task.id})

  else:
    form = HeightProcessForm()

  return render(request, 'order/dem_error/html/make_order.html',
                {'title': 'Voxel Globe - DEM Error Calculation',
                 'page_title': 'Voxel Globe - DEM Error Calculation',
                 'form':form})

def order_status(request, task_id):
  from celery.result import AsyncResult
  
  task = AsyncResult(task_id)

  return render(request, 'task/html/task_3d_error_results.html',
                {'title': 'Voxel Globe - DEM Error Results',
                 'page_title': 'Voxel Globe - DEM Error Results',
                 'task': task})
