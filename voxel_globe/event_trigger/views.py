from django.shortcuts import render, redirect

from .forms import EventTriggerForm

def event_trigger_results(request):
  if request.method == 'POST':
    pass
  else:
    return render(request, 'event_trigger/html/event_trigger_results.html',
                  {'title': 'Voxel Globe - Event Trigger Results',
                   'page_title': 'Event Trigger Results'})

def create_event_trigger(request):
  import voxel_globe.meta.models as models
  from django.contrib.gis.geos import Point
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
  vpgl_camera = vpgl_adaptor.load_rational_camera_from_txt(camera.rpc_path)[1]
  initial_guess = np.mean(image.attributes['planet_rest_response']['geometry']['coordinates'][0][0:4], axis=0)
  initial_guess = np.hstack((initial_guess, 0)) #elevation guess is 0

  new_points = []

  altitude = 0

  lvcs = vpgl_adaptor.create_lvcs(27.109287683,56.0671097675,0.0, "wgs84")

  import vsi.tools.vdb_rpdb2 as vdb; vdb.set_trace(fAllowRemote=True)

  for point in points:
    point = vpgl_adaptor.get_rpc_backprojected_ray(vpgl_camera, point[0], point[1], altitude,
                                                   initial_guess[0], 
                                                   initial_guess[1], 
                                                   initial_guess[2])
    point = vpgl_adaptor.convert_to_local_coordinates2(lvcs, point[1], point[0], point[2])
    point = (point[1], point[0], point[2])

    new_points.append(point)

  event_geometry_filepath = write_ply_file(new_points)

  reference_geometry = models.SattelGeometryObject(origin=Point(56.0671097675,27.109287683,0.0),
                                       geometry_path='/opt/vip/mesh_1.ply',
                                       site_id=site_id, name='Reference Object for %s' % site.name)
  reference_geometry.attributes['web'] = 'True'
  reference_geometry.save()

  event_geometry = models.SattelGeometryObject(origin=Point(56.0671097675,27.109287683,0.0),
                                       #geometry_path=event_geometry_filepath,
                                       geometry_path='/opt/vip/mesh_2.ply',
                                       site_id=site_id, name='Event Object for %s' % site.name)
  event_geometry.attributes['web'] = 'True'
  event_geometry.save()

  event_trigger = models.SattelEventTrigger(origin=Point(56.0671097675,27.109287683,0.0),
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
          args=(form.data['site'],))

      return render(request, 'task/html/task_started.html',
                    {'title': 'Voxel Globe - Event Trigger',
                     'page_title': 'Event Trigger',
                     'task_id':task.id})
  
  else:
    form = EventTriggerForm()

  return render(request, 'event_trigger/html/make_order.html',
                {'title': 'Voxel Globe - Event Trigger',
                 'page_title': 'Event Trigger',
                 'form':form})

def eventTriggerCreator(request):
    return render(request, 'view_event_trigger/html/eventTriggerCreator.html')

def write_ply_file(points):
  '''
  Given a string of comma-separated values that represent 2d points, parse
  the string, create a ply file in the temp storage directory representing
  the shape formed by the string, and return the filepath.
  '''

  import voxel_globe.tools
  import os
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