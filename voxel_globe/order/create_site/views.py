from django.shortcuts import render, redirect
from .forms import CreateSiteForm

def make_order(request):
  if request.method == 'POST':
    form = CreateSiteForm(request.POST)

    if form.is_valid():
      image_id = form.data['image']

      return redirect('main:index')
  else:
    form = CreateSiteForm()

  return render(request, 'order/create_site/html/make_order.html',
                {'title': 'Voxel Globe - Create Site',
                 'page_title': 'Voxel Globe - Create Site',
                 'form':form})