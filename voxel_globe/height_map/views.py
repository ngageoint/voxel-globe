from django.shortcuts import render, redirect
# Create your views here. Mostly placeholders

from .forms import HeightProcessForm

from .forms import HeightForm

def make_height_map(request):
  if request.method == 'POST':

    form = HeightForm(request.POST)

    if form.is_valid():
      import voxel_globe.height_map.tasks as tasks

      task = tasks.create_height_map.apply_async(
          args=(form.data['voxel_world'],form.cleaned_data['render_height']),
          user=request.user)
      auto_open = True

  else:
    form = HeightForm()
    auto_open = False

  return render(request, 'height_map/html/make_height_map.html',
                {'form':form,
                 'task_menu_auto_open': auto_open})

def calculate_dem_error(request):
  if request.method == 'POST':

    form = HeightProcessForm(request.POST)

    if form.is_valid():
      import voxel_globe.height_map.tasks as tasks

      image_id = form.data['image']

      task = tasks.height_map_error.apply_async(args=(image_id,), user=request.user)
      auto_open = True
  else:
    form = HeightProcessForm()
    auto_open = False

  return render(request, 'height_map/html/calculate_dem_error.html',
                {'title': 'Voxel Globe - DEM Error Calculation',
                 'page_title': 'DEM Error Calculation',
                 'form':form,
                 'task_menu_auto_open': auto_open})

def order_status(request, task_id):
  from celery.result import AsyncResult

  task = AsyncResult(task_id)

  return render(request, 'task/html/task_3d_error_results.html',
                {'title': 'Voxel Globe - DEM Error Results',
                 'page_title': 'DEM Error Results',
                 'task': task})
