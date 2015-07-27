from django.shortcuts import render
# Create your views here. Mostly placeholders

def index(request):
    return render(request, 'main/html/index.html')

def voxelCreator(request):
    return render(request, 'main/html/voxelCreator.html')

def voxelWorldViewer(request):
    return render(request, 'main/html/voxelWorldViewer.html')
