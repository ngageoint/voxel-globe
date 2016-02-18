from django.shortcuts import render
# Create your views here. Mostly placeholders

from .forms import HeightForm

def make_order(request):
  if request.method == 'POST':

    form = HeightForm(request.POST)

    if form.is_valid():
      import voxel_globe.height_map.tasks as tasks

      voxel_world_id = form.data['voxel_world']

      task = tasks.create_height_map.apply_async(args=(voxel_world_id,))

      return render(request, 'task/html/task_started.html',
                    {'title': 'Voxel Globe - Height Map Ordered',
                     'page_title': 'Voxel Globe - Height Map Ordered',
                     'task_id':task.id})
  
  else:
    form = HeightForm()

  return render(request, 'order/height_map/html/make_order.html',
                {'form':form})
