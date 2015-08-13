from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

# Create your views here.

def fetch_point_cloud(request):
  import json
  from voxel_globe.serializers.numpyjson import NumpyAwareJSONEncoder
  import numpy as np
  from plyfile import PlyData
  from voxel_globe.meta import models
  import os

  import boxm2_adaptor
  from boxm2_scene_adaptor import boxm2_scene_adaptor
  from vpgl_adaptor import convert_local_to_global_coordinates

  request_data = request.POST
  voxel_world_id = int(request_data["voxelWorldId"])
  number_points = int(request_data.get("points", 100))
  if 1:
#  try:
    voxel_world = models.VoxelWorld.objects.get(id=voxel_world_id)

    #replace this with create_lvcs
    scene =  boxm2_scene_adaptor(os.path.join(voxel_world.voxel_world_dir, 'scene.xml'), 'cpp')
    lvcs = scene.lvcs

    ply = PlyData.read(str(os.path.join(voxel_world.voxel_world_dir, 'model.ply')))
    data = ply.elements[0].data
    
    lla = np.zeros((len(data['x']), 3))
    for x in xrange(len(data['x'])):
      lla[x,:] = convert_local_to_global_coordinates(lvcs, data['x'][x], data['y'][x], data['z'][x]);

    latitude = lla[:,0]
    longitude = lla[:,1]
    altitude = lla[:,2]
    color = map(lambda r,b,g:'0x%02x%02x%02x' % (r, g, b), data['red'], data['green'], data['blue'])

  '''except:
    ## Hack-a-code
    np.random.seed(voxel_world_id)
    latitude = float(request_data.get("latitude", 40.423256522222))+(np.random.rand(number_points)*2-1)*0.01
    longitude = float(request_data.get("longitude", -86.913520311111))+(np.random.rand(number_points)*2-1)*0.01
    altitude =  float(request_data.get("altitude", 200))+(np.random.rand(number_points)*2-1)*50
    color = 0 '''

  points = {"latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "color": color}

  return HttpResponse(json.dumps(points, cls=NumpyAwareJSONEncoder),
                       content_type="application/json")
