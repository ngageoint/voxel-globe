from django.shortcuts import render
# Create your views here. Mostly placeholders

def index(request):
    return render(request, 'main/html/index.html')

# ANDY, should these be deleted?
def voxelCreator(request):
    return render(request, 'main/html/voxelCreator.html')

# ANDY, should these be deleted?
def voxelWorldViewer(request):
    return render(request, 'main/html/voxelWorldViewer.html')
