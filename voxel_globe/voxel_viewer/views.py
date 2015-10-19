from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from .tools import get_point_cloud

# Create your views here.

def fetch_point_cloud(request):
  import json
  from voxel_globe.serializers.numpyjson import NumpyAwareJSONEncoder
  import numpy as np

  request_data = request.GET
  voxel_world_id = int(request_data["voxelWorldId"])
  number_points = int(request_data.get("points", 100))
  if voxel_world_id>0:
    points = get_point_cloud(voxel_world_id, number_points)
    points['le'] = (np.random.random(len(points['latitude']))*6).tolist()
    points['ce'] = (np.random.random(len(points['latitude']))*6).tolist()
  else:
     ## Hack-a-code
     np.random.seed(-voxel_world_id)
     latitude = float(request_data.get("latitude", 40.423256522222))+(np.random.rand(number_points)*2-1)*0.01
     longitude = float(request_data.get("longitude", -86.913520311111))+(np.random.rand(number_points)*2-1)*0.01
     altitude =  float(request_data.get("altitude", 200))+(np.random.rand(number_points)*2-1)*50
     color = ('#909090',)*number_points

     points = {"latitude": latitude,
               "longitude": longitude,
               "altitude": altitude,
               "color": color,
               "le": [2]*number_points,
               "ce": [1.5]*number_points}

  return HttpResponse(json.dumps(points, cls=NumpyAwareJSONEncoder),
                       content_type="application/json")

def view_point_cloud(request):
  from voxel_globe.meta import models
  voxel_world_list = models.VoxelWorld.objects.all();
  response = render(request, 'view_voxel_world/html/make_view_1.html', 
                {'voxel_world_list':voxel_world_list});
  return response

def ingest_point_cloud(request):
  request_data = request.POST
  voxel_world_id = int(request_data["id"]);
  points = get_point_cloud(voxel_world_id)
  response = render(request, 'view_voxel_world/html/done.html');
  return response

def display_voxel_world(request):
  return render(request, 'view_voxel_world/html/voxelWorldViewer.html')
