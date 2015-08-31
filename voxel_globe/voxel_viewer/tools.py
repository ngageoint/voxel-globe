

def get_point_cloud(voxel_world_id, history=None):
  from voxel_globe.meta import models
  from vpgl_adaptor import convert_local_to_global_coordinates_array, create_lvcs
  import os
  import numpy as np
  from plyfile import PlyData

  voxel_world = models.VoxelWorld.objects.get(id=voxel_world_id).history(history)

  lvcs = create_lvcs(voxel_world.origin[1], voxel_world.origin[0], voxel_world.origin[2], 'wgs84')

  ply = PlyData.read(str(os.path.join(voxel_world.voxel_world_dir, 'model.ply')))
  data = ply.elements[0].data
  
  lla = convert_local_to_global_coordinates_array(lvcs, data['x'].tolist(), data['y'].tolist(), data['z'].tolist());

  latitude = np.array(lla[0])
  longitude = np.array(lla[1])
  altitude = np.array(lla[2])
  color = map(lambda r,b,g:'0x%02x%02x%02x' % (r, g, b), data['red'], data['green'], data['blue'])
  return {"latitude": latitude,
          "longitude": longitude,
          "altitude": altitude,
          "color": color}
