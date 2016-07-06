from django.shortcuts import render, redirect

def image_view(request):
  if request.method == 'POST':
    pass
  else:
    return render(request, 'image_view/html/image_view.html',
                  {'title': 'Voxel Globe - Image View',
                   'page_title': 'Image View'})

# Create your views here.
