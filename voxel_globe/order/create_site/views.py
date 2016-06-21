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