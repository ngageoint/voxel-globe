from django.shortcuts import render
# Create your views here. Mostly placeholders

from .forms import HeightForm

def make_order(request):
  if request.method == 'POST':

    form = HeightForm(request.POST)

    if form.is_valid():
      import voxel_globe.height_map.tasks as tasks

      task = tasks.create_height_map.apply_async(
          args=(form.data['voxel_world'],form.cleaned_data['render_height']),
          user=request.user)
      auto_open = True

      # return render(request, 'task/html/task_started.html',
      #               {'title': 'Voxel Globe - Height Map Ordered',
      #                'page_title': 'Height Map Ordered',
      #                'task_id':task.id})
  
  else:
    form = HeightForm()
    auto_open = False

  return render(request, 'order/height_map/html/make_order.html',
                {'form':form,
                 'task_menu_auto_open': auto_open})
