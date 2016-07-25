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

  name = request.POST['name']
  image_id = int(request.POST['image_id'])
  image_set_id = int(request.POST['image_set_id'])
  points = request.POST['points']
  site_id = int(request.POST['site_id'])

  site = models.SattelSite.objects.get(id=site_id)

  # TODO
  points = "1250.390625,-2507.2265625,2771.484375,-1076.3671875,4730.859375,-1579.1015625,3171.09375,-3551.3671875,1250.390625,-2507.2265625"
  write_ply_file(points, "/opt/vip/mesh_1.ply")  # nope. with storage_dir etc.

  reference_geometry = models.SattelGeometryObject(origin=Point(56.0671097675,27.109287683,0.0),
                                       geometry_path='/opt/vip/mesh_1.ply',
                                       site_id=site_id, name='Reference Object for %s' % site.name)
  reference_geometry.attributes['web'] = 'True'
  reference_geometry.save()

  event_geometry = models.SattelGeometryObject(origin=Point(56.0671097675,27.109287683,0.0),
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
  points = points.split(',')
  length = len(points)

  # must be even-numbered, since every even value is x and every odd is y
  if not length % 2 == 0:
    return
  
  points_array = []
  ordered_indices = []
  
  for k in range(0, length, 2):
    x = points[k]
    y = points[k + 1]
    z = 0.0
    point = (x, y, z)
    points_array.append(point)
    ordered_indices.append(k/2)
    
  import voxel_globe.tools
  import os
  with voxel_globe.tools.storage_dir('event_trigger_ply') as ply_dir:
    num_files = len([name for name in os.listdir(ply_dir)])
    filepath = os.path.join(ply_dir, 'mesh_%d.ply' % num_files)
  
  import numpy
  import plyfile
  from plyfile import PlyData, PlyElement
  
  vertex = numpy.array(points_array,
                      dtype=[('x', 'double'), ('y', 'double'),
                             ('z', 'double')])
  face = numpy.array([(ordered_indices,)], [('vertex_indices', '|O')])
  el1 = PlyElement.describe(vertex, 'vertex')
  el2 = PlyElement.describe(face, 'face')
  
  PlyData([el1, el2], text=True, comments=['mesh-feature'], 
    obj_info=['a bmsh3d_mesh object']).write(filepath)
  return filepath