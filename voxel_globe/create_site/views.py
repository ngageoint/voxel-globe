from django.shortcuts import render, redirect
from .forms import CreateSiteForm

def make_order(request):
  if request.method == 'POST':
    from voxel_globe.create_site import tasks
    sattel_site_id = int(request.POST.get('sattel_site_id', -1))
    task = tasks.create_site.apply_async(args=([sattel_site_id]), user=request.user)
    auto_open = True

  else:
    auto_open = False

  form = CreateSiteForm()

  return render(request, 'create_site/html/make_order.html',
                {'title': 'Voxel Globe - Create Site',
                 'page_title': 'Create Site',
                 'form':form,
                 'task_menu_auto_open': auto_open})