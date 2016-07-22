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


# Create your views here.
def eventTriggerCreator(request):
    return render(request, 'view_event_trigger/html/eventTriggerCreator.html')

