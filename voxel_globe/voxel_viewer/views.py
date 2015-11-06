from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

# Create your views here.

def fetch_point_cloud(request):
  import json
  from voxel_globe.serializers.numpyjson import NumpyAwareJSONEncoder
  import numpy as np

  request_data = request.GET
  voxel_world_id = int(request_data["voxelWorldId"])
  number_points = request_data.get("points", None)
  try:
    number_points = int(number_points)
  except:
    pass

  if voxel_world_id>0:
    points = get_point_cloud(voxel_world_id, number_points)
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

def display_voxel_world(request):
  return render(request, 'view_voxel_world/html/voxelWorldViewer.html')
