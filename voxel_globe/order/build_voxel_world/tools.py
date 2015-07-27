from boxm2_adaptor import create_scene_and_blocks
from vpgl_adaptor import create_lvcs, convert_local_to_global_coordinates

def create_scene(origin, lla1, lla2, scene_size, scene_dir, vox_size=1,
                 block_len_xy = 100, block_len_z = 60):
  ''' Inputs
      origin, lla1, lla2 - 3 array - longitude, latitude, and altitude in
                           degrees and meters
      scene_size - 3 array, x(east/west), y(north/south) and z(height) in 
                   meters
      vox_size in meters
      scene_dir - directory to write scene.xml in,
      block_xy - in meters
      block_z - in meters'''

  app_model = "boxm2_mog3_grey";
  obs_model = "boxm2_num_obs";
  xml_name_prefix = "scene";
  create_scene_and_blocks(scene_dir, app_model, obs_model, 
                          origin[0], origin[1], origin[2], 
                          lla1[0], lla1[1], lla[2], 
                          lla[0], lla[1], lla[2], 
                          vox_size, block_len_xy, block_len_z, "utm", 1, 
                          xml_name_prefix);


