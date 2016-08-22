from django.shortcuts import render, redirect

from .forms import EventTriggerForm

import os

def event_trigger_results(request):
  if request.method == 'POST':
    pass
  else:
    return render(request, 'event_trigger/html/event_trigger_results.html',
                  {'title': 'Voxel Globe - Event Trigger Results',
                   'page_title': 'Event Trigger Results'})

def update_geometry_polygon(request):
  import voxel_globe.meta.models as models
  from django.contrib.gis.geos import Point, Polygon, GEOSGeometry
  import numpy as np
  import brl_init
  import vpgl_adaptor_boxm2_batch as vpgl_adaptor

  image_id = int(request.POST['image_id'])
  points = GEOSGeometry(request.POST['points'])
  sattelgeometryobject_id = int(request.POST['sattelgeometryobject_id'])
  site_id = int(request.POST['site_id'])
  projection_mode = request.POST['projection_mode']

  site = models.SattelSite.objects.get(id=site_id)
  image = models.Image.objects.get(id=image_id)
  camera = image.camera_set.filter(cameraset=site.camera_set).select_subclasses('rpccamera')[0]
  sattelgeometryobject = models.SattelGeometryObject.objects.get(id=sattelgeometryobject_id)

  vpgl_camera = vpgl_adaptor.load_rational_camera_from_txt(camera.rpc_path)
  initial_guess = np.mean(image.attributes['planet_rest_response']['geometry']['coordinates'][0][0:4], axis=0)
  initial_guess = np.hstack((initial_guess, 0)) #elevation guess is 0

  lvcs_points = []

  gps_points = []

  if projection_mode == "z-plane":
    projection_height = float(request.POST['height'])

    for point in points.coords[0]:
      point = vpgl_adaptor.get_rpc_backprojected_ray(vpgl_camera, 
                                                     point[0], point[1], 
                                                     projection_height,
                                                     initial_guess[0], 
                                                     initial_guess[1], 
                                                     initial_guess[2])
      gps_points.append(point)


  origin = np.array(gps_points).mean(axis=0)

  lvcs = vpgl_adaptor.create_lvcs(origin[1], origin[0], origin[2], "wgs84")
  origin = Point(*origin)

  for point in gps_points:
    point = vpgl_adaptor.convert_to_local_coordinates2(lvcs, point[1], point[0], point[2])

    lvcs_points.append(point)

  print sattelgeometryobject.geometry_path

  if sattelgeometryobject.geometry_path and os.path.exists(sattelgeometryobject.geometry_path):
    os.remove(sattelgeometryobject.geometry_path)

  geometry_filepath = write_ply_file(lvcs_points)
  sattelgeometryobject.geometry_path=geometry_filepath
  sattelgeometryobject.origin = origin
  sattelgeometryobject.geometry = Polygon(gps_points+gps_points[0:1])
  sattelgeometryobject.save()
  from django.shortcuts import HttpResponse
  return HttpResponse('{}')

def get_event_geometry(request):
  import json
  from django.shortcuts import HttpResponse
  import voxel_globe.meta.models as models
  import brl_init
  import vpgl_adaptor_boxm2_batch as vpgl_adaptor

  image_id = int(request.GET['image_id'])
  site_id = int(request.GET['site_id'])
  sattelgeometryobject_id = int(request.GET['sattelgeometryobject_id'])

  image = models.Image.objects.get(id=image_id)
  site = models.SattelSite.objects.get(id=site_id)
  camera = image.camera_set.filter(cameraset=site.camera_set).select_subclasses('rpccamera')[0]
  vxl_camera = vpgl_adaptor.load_rational_camera_from_txt(camera.rpc_path)

  sattelgeometryobject = models.SattelGeometryObject.objects.get(id=sattelgeometryobject_id)
  polygon = sattelgeometryobject.geometry

  points = []

  for coord in polygon.coords[0]:
    points.append(vpgl_adaptor.project_point(vxl_camera, *coord))

  up_vector = vpgl_adaptor.rational_camera_get_up_vector(vxl_camera)

  response = {'points':points, 'up':up_vector}

  return HttpResponse(json.dumps(response))

def get_site_geometry(request):
  import json
  from django.shortcuts import HttpResponse
  import voxel_globe.meta.models as models
  import brl_init
  import vpgl_adaptor_boxm2_batch as vpgl_adaptor

  image_id = int(request.GET['image_id'])
  site_id = int(request.GET['site_id'])

  image = models.Image.objects.get(id=image_id)
  site = models.SattelSite.objects.get(id=site_id)
  camera = image.camera_set.filter(cameraset=site.camera_set).select_subclasses('rpccamera')[0]
  vxl_camera = vpgl_adaptor.load_rational_camera_from_txt(camera.rpc_path)

  x1 = site.bbox_min[0]
  y1 = site.bbox_min[1]
  x2 = site.bbox_max[0]
  y2 = site.bbox_max[1]
  z = site.bbox_min[2]

  points = []
  coords = [[x1,y1,z], 
            [x1,y2,z],
            [x2,y2,z],
            [x2,y1,z],
            [x1,y1,z]]

  for coord in coords:
    points.append(vpgl_adaptor.project_point(vxl_camera, *coord))

  return HttpResponse(json.dumps(points))


def create_event_trigger(request):
  import voxel_globe.meta.models as models
  from django.contrib.gis.geos import Point, Polygon
  import numpy as np
  import brl_init
  import vpgl_adaptor_boxm2_batch as vpgl_adaptor

  name = request.POST['name']
  image_id = int(request.POST['image_id'])
  #image_set_id = int(request.POST['image_set_id'])
  points = np.fromstring(request.POST['points'], dtype=float, sep=',').reshape((-1, 2))
  site_id = int(request.POST['site_id'])

  site = models.SattelSite.objects.get(id=site_id)
  image = models.Image.objects.get(id=image_id)
  camera = image.camera_set.get(cameraset=site.camera_set).select_subclasses()[0] #REDO
  vpgl_camera = vpgl_adaptor.load_rational_camera_from_txt(camera.rpc_path)
  initial_guess = np.mean(image.attributes['planet_rest_response']['geometry']['coordinates'][0][0:4], axis=0)
  initial_guess = np.hstack((initial_guess, 0)) #elevation guess is 0

  new_points = []

  altitude = 0

  gps_points = []

  for point in points:
    point = vpgl_adaptor.get_rpc_backprojected_ray(vpgl_camera, point[0], point[1], altitude,
                                                   initial_guess[0], 
                                                   initial_guess[1], 
                                                   initial_guess[2])
    gps_points.append(point)

  origin = np.array(gps_points).mean(axis=0)
  lvcs = vpgl_adaptor.create_lvcs(origin[1], origin[0], origin[2], "wgs84")
  origin = Point(*origin)
  
  for point in gps_points:
    point = vpgl_adaptor.convert_to_local_coordinates2(lvcs, point[1], point[0], point[2])

    new_points.append(point)

  event_geometry_filepath = write_ply_file(new_points)


  # TOTAL DEMO HACK REDO  
  reference_points_global = [(27.091768977238363, 56.0750234815191, 0.0),
                             (27.09267315902605, 56.07801120928596, 0.0),
                             (27.09515736555473, 56.07976470925469, 0.0),
                             (27.095800018351348, 56.07769799176195, 0.0),
                             (27.09547881983413, 56.075027771901226, 0.0),
                             (27.093305684249717, 56.07240140862926, 0.0)] #latitude longitude order!!!
  reference_points_local = []
  for point in reference_points_global:
    reference_points_local.append(vpgl_adaptor.convert_to_local_coordinates2(lvcs, *point))
 
  reference_geometry_filepath = write_ply_file(reference_points_local)
  #END OF HACK

  reference_geometry = models.SattelGeometryObject(origin=origin,
                                       geometry_path=reference_geometry_filepath,
                                       site_id=site_id, name='Reference Object for %s' % site.name)
  reference_geometry.attributes['web'] = 'True'
  reference_geometry.save()

  event_geometry = models.SattelGeometryObject(origin=origin,
                                       geometry_path=event_geometry_filepath,
                                       site_id=site_id, name='Event Object for %s' % site.name)
  event_geometry.geometry = Polygon(gps_points)
  event_geometry.attributes['web'] = 'True'
  event_geometry.save()

  event_trigger = models.SattelEventTrigger(origin=origin,
                                            site_id=site_id, name=name,
                                            reference_image_id=image_id)
  event_trigger.attributes['web'] = 'True'
  event_trigger.save()

  event_trigger.event_areas.add(event_geometry)
  event_trigger.reference_areas.add(reference_geometry)

  from django.shortcuts import HttpResponse
  return HttpResponse(event_trigger.id)

def run_event_trigger(request):
  if request.method == 'POST':

    form = EventTriggerForm(request.POST)

    if form.is_valid():
      import voxel_globe.event_trigger.tasks as tasks

      task = tasks.event_trigger.apply_async(
          args=(form.data['site'],), user=request.user)

      auto_open = True
  
  else:
    form = EventTriggerForm()
    auto_open = False

  return render(request, 'event_trigger/html/make_order.html',
                {'title': 'Voxel Globe - Event Trigger',
                 'page_title': 'Event Trigger',
                 'form':form,
                 'task_menu_auto_open': auto_open})

def eventTriggerCreator(request):
    return render(request, 'view_event_trigger/html/eventTriggerCreator.html')

def write_ply_file(points):
  '''
  Given a string of comma-separated values that represent 2d points, parse
  the string, create a ply file in the temp storage directory representing
  the shape formed by the string, and return the filepath.
  '''

  import voxel_globe.tools
  with voxel_globe.tools.storage_dir('event_trigger_ply') as ply_dir:
    num_files = len([name for name in os.listdir(ply_dir)])
    filepath = os.path.join(ply_dir, 'mesh_%d.ply' % num_files)
  
  import numpy
  import plyfile
  from plyfile import PlyData, PlyElement
  
  vertex = numpy.array(points,
                      dtype=[('x', 'double'), ('y', 'double'),
                             ('z', 'double')])
  face = numpy.array([(range(len(points)),)], [('vertex_indices', '|O')])
  el1 = PlyElement.describe(vertex, 'vertex')
  el2 = PlyElement.describe(face, 'face')
  
  PlyData([el1, el2], text=True, comments=['mesh-feature'], 
    obj_info=['a bmsh3d_mesh object']).write(filepath)

  return filepath