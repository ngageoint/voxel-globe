from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def tiePointCreator(request):
    return render(request, 'tiepoint/html/tiePointCreator.html')

def fetchCameraRay(request):
  import voxel_globe.tiepoint.tasks
  
  points = voxel_globe.tiepoint.tasks.fetchCameraRay(**request.REQUEST);
  
  return HttpResponse(points);

def fetchCameraFrustum(request):
  import voxel_globe.tiepoint.tasks

  points = voxel_globe.tiepoint.tasks.fetchCameraFrustum(**request.REQUEST);
  
  return HttpResponse(points);
