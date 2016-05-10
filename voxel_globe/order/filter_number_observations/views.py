from django.shortcuts import render, redirect
from .forms import FilterNumberObservationsForm

def make_order(request):
  if request.method == 'POST':
    form = FilterNumberObservationsForm(request.POST)

    if form.is_valid():
      import voxel_globe.filter_number_observations.tasks as tasks

      voxel_world_id = form.data['voxel_world']
      mean_multiplier = form.cleaned_data['number_means']

      task = tasks.filter_number_observations.apply_async(args=(voxel_world_id,mean_multiplier))

      return redirect('filter_number_observations:order_status', task_id=task.id)
  else:
    form = FilterNumberObservationsForm(initial={'number_means':3})

  return render(request, 'order/filter_number_observations/html/make_order.html',
                {'title': 'Voxel Globe - Filter Number Observations',
                 'page_title': 'Voxel Globe - Filter Number Observations',
                 'form':form})

def order_status(request, task_id):
  from celery.result import AsyncResult
  
  task = AsyncResult(task_id)

  return render(request, 'order/filter_number_observations/html/order_status.html',
                {'title': 'Voxel Globe - Filter Number Observations Status',
                 'page_title': 'Voxel Globe - Filter Number Observations Status',
                 'task': task})
