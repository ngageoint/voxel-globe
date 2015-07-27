from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

# Create your views here.

def fetch_point_cloud(request):
  import json
  from voxel_globe.serializers.numpyjson import NumpyAwareJSONEncoder
  import numpy as np
  request_data = request.POST
  voxel_world_id = int(request_data["voxelWorldId"])
  number_points = int(request_data.get("points", 100))

  ## Hack-a-code
  np.random.seed(voxel_world_id)
  latitude = float(request_data.get("latitude", 40.423256522222))+(np.random.rand(number_points)*2-1)*0.01
  longitude = float(request_data.get("longitude", -86.913520311111))+(np.random.rand(number_points)*2-1)*0.01
  altitude =  float(request_data.get("altitude", 200))+(np.random.rand(number_points)*2-1)*50

  points = {"latitude": latitude,
            "longitude": longitude,
            "altitude": altitude}

  return HttpResponse(json.dumps(points, cls=NumpyAwareJSONEncoder),
                       content_type="application/json")
