import os
import json


from celery.utils.log import get_task_logger


from vsi.iglob import glob as iglob


logger = get_task_logger(__name__);

#Move to ingest.tools when done devving
def match_images(images, camera_names, json_config={}):
  ''' returns dictionary camera_name:image pairs 

      json example:
      {"image_camera_match":
        {"frame_00008.png": "frame_00001.txt",
         "frame_00019.png": "frame_00002.txt",
         "frame_00022.png": "frame_00003.txt"}
      }
      '''

  matches = {}

  try:
    json_config=json_config['image_camera_match']
  except (TypeError, KeyError):
    json_config={}

  #lowercase everything... THANK YOU WINDOWS! 8:(
  camera_safe_names_ext = [x.lower() for x in camera_names]
  camera_safe_names = [os.path.splitext(x)[0] for x in camera_safe_names_ext]
  image_safe_names_ext = [s.original_filename.lower() for s in images]

  json_image_safe_names = [s.lower() for s in json_config]

  for image_index, image in enumerate(images):
    #First check the json_config to see if the camera/image is defined there.
    #This takes priority
    try:
      json_image_index = json_image_safe_names.index(image_safe_names_ext[image_index])
      json_image_name = json_config.keys()[json_image_index]
      json_camera_name = json_config[json_image_name]
      camera_index = camera_safe_names_ext.index(json_camera_name.lower())
      camera_name = camera_names[camera_index]
      matches[camera_name] = image
      continue
    except ValueError:
      pass

    #Second, guess that the filenames without extension match
    try:
      image_name = os.path.splitext(image_safe_names_ext[image_index])[0]
      #strip the extension to check against camera name
      camera_index = camera_safe_names.index(image_name)
      camera_name = camera_names[camera_index]
      matches[camera_name] = image
      continue
    except ValueError:
      pass

    logger.debug('No camera matched for %s', image.original_filename)

  #Third if there are NO matches, guess that when sorted in lowered alpha order
  #that they match that way... NOT the best, but it's a nice idea...
  if not matches:
    from vsi.tools.natural_sort import natural_sorted
    camera_indexes = [i[0] for i in natural_sorted(
        enumerate(camera_safe_names_ext), key=lambda x:x[1])]
    image_indexes = [i[0] for i in natural_sorted(
        enumerate(image_safe_names_ext), key=lambda x:x[1])]
    number_matches = min(len(camera_indexes), len(image_indexes))

    for match_index in range(number_matches):
      image_index = image_indexes[match_index]
      camera_index = camera_indexes[match_index]
      matches[camera_names[camera_index]] = images[image_index]

  logger.info('%d out of %d images matched to cameras', len(matches), 
              len(images))

  return matches

def load_voxel_globe_metadata(directory_or_filename='ingest_voxel_globe.json'):
  ''' Loads the ingest_voxel_globe json file

      Will read in the json configuration file for the ingest. The argument can
      be a case sensitive filename, or a directory where a case insensitive 
      search for filename 'ingest_voxel_globe.json' will be loaded

      Arguments
      directory_or_filename - Directory containing ingest_voxel_globe.json or
                              filename of json file

      Return
      Dictionary of json object, or None if file not found '''

  if os.path.isdir(directory_or_filename):
    filename = iglob(os.path.join(directory_or_filename, 
                                  'ingest_voxel_globe.json'), False)

  else:
    if os.path.exists(directory_or_filename):
      filename = [directory_or_filename]
    else:
      return None

  config = None

  for match_ifilename in filename: #Case insensitive
    with open(match_ifilename, 'r') as fid:
      config = json.load(fid)

  return config
