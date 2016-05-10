from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

# Create your views here.

def fetch_point_cloud(request):
  import json
  from voxel_globe.serializers.numpyjson import NumpyAwareJSONEncoder
  import numpy as np

  from .tools import get_point_cloud

  request_data = request.GET
  point_cloud_id = int(request_data["pointCloudId"])
  number_points = request_data.get("points", None)
  try:
    number_points = int(number_points)
  except:
    pass

  points = get_point_cloud(point_cloud_id, number_points)

  return HttpResponse(json.dumps(points, cls=NumpyAwareJSONEncoder),
                      content_type="application/json")

def display_voxel_world(request):
  return render(request, 'view_voxel_world/html/voxelWorldViewer.html')

def display_potree_world(request):
  return render(request, 'view_voxel_world/html/potreeWorldViewer.html')

def display_potree_demo(request):
  return render(request, 'view_voxel_world/html/potreeDemo.html')

def display_potree_viewer(request):
  return render(request, 'view_voxel_world/html/potreeViewer.html')
