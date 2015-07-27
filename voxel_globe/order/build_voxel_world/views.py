from django.shortcuts import render
from django.http import HttpResponse

from uuid import uuid4

from voxel_globe.meta import models
from voxel_globe.meta.tools import getHistory
from .models import Session

# Create your views here.
def make_order_1(request):
  uuid = uuid4()
  session = Session(uuid=uuid, owner=request.user);
  session.save();

  image_collection_list = models.ImageCollection.objects.all();
  response = render(request, 'order/build_voxel_world/html/make_order_1.html', 
                {'image_collection_list':image_collection_list});
  response.set_cookie('order_build_voxel_world_uuid', uuid, max_age=15*60)
  return response

def make_order_2(request, image_collection_id):
  #Choose the scene
  scene_list = models.Scene.objects.all()

  return render(request, 'order/build_voxel_world/html/make_order_2.html',
                {'scene_list':scene_list,
                 'image_collection_id':image_collection_id})

def make_order_3(request, image_collection_id, scene_id):
  import voxel_globe.tools.enu as enu
  from voxel_globe.tools.camera import get_llh
  import numpy as np
  
  image_collection = models.ImageCollection.objects.get(id=image_collection_id)
  image_list = image_collection.images.all()
  scene = models.Scene.objects.get(id=scene_id);

  geolocated = scene.geolocated

  # #if min==max, they are probably all zeros and the bounding box isn't set yet
  # if scene.bbox_min == scene.bbox_max:
  #   #TODO: Replace this with bundle2scene in visualsfm task
  #   llhs = []
  
  #   for image in image_list:
  #     llhs.append(get_llh(image.history()))

  #   llhs = np.array(llhs)
  #   bbox_min = llhs.min(axis=0)
  #   bbox_max = llhs.max(axis=0)

  #   #The above code calculated the bounding box of the cameras. Set the 
  #   #bounding box of the scene to be from the bottom of the lowest camera to
  #   #down to sea level. Hard to do anything else intelligently
  #   bbox_max[2] = bbox_min[2]
  #   bbox_min[2] = 0
  #   voxel_size = 1
  # else:
  bbox_min = scene.bbox_min
  bbox_max = scene.bbox_max
  voxel_size = sum(scene.default_voxel_size.coords)/3.0

  #if geolocated, convert lvcs to lla
  if geolocated:
    from vpgl_adaptor import create_lvcs, convert_local_to_global_coordinates
    origin = scene.origin.coords
    lvcs = create_lvcs(origin[1], origin[0], origin[2], "wgs84");
    (bbox_min[1], bbox_min[0], bbox_min[2]) = convert_local_to_global_coordinates(lvcs,bbox_min[1], bbox_min[0], bbox_min[2])
    (bbox_max[1], bbox_max[0], bbox_max[2]) = convert_local_to_global_coordinates(lvcs,bbox_max[1], bbox_max[0], bbox_max[2])

  bbox = {'x_min':bbox_min[0],
          'x_max':bbox_max[0],
          'y_min':bbox_min[1],
          'y_max':bbox_max[1],
          'z_min':bbox_min[2],
          'z_max':bbox_max[2]}

  
  return render(request, 'order/build_voxel_world/html/make_order_3.html',
                {'scene_id':scene_id, 'bbox':bbox, 'geolocated':geolocated,
                 'voxel_size': voxel_size,
                 'image_collection_id':image_collection_id})


def make_order_4(request, image_collection_id, scene_id):
  from voxel_globe.build_voxel_world import tasks
  
  try:
    uuid = request.COOKIES['order_build_voxel_world_uuid'];
    session = Session.objects.get(uuid=uuid);
    session.delete();
  except:
    response = HttpResponse('Session Expired')
    try:
      response.delete_cookie('order_build_voxel_world_uuid')
    finally:
      return response;

  history = getHistory(request.REQUEST.get('history', None))

  scene = models.Scene.objects.get(id=scene_id);

  bbox = {'x_min': request.POST['x_min'], 
          'y_min': request.POST['y_min'], 
          'z_min': request.POST['z_min'], 
          'x_max': request.POST['x_max'], 
          'y_max': request.POST['y_max'], 
          'z_max': request.POST['z_max'],
          'voxel_size': request.POST['voxel_size'],
          'geolocated': scene.geolocated}
  
  skipFrames = int(request.POST['skip_frames'])

  t = tasks.run_build_voxel_model.apply_async(args=(image_collection_id, 
      scene_id, bbox, skipFrames, True, history))

  #Crap ui filler   
  image_collection = models.ImageCollection.objects.get( \
      id=image_collection_id);
  image_list = image_collection.images;
  #WARNING, Source of History error, but images shouldn't change!?

  #CALL THE CELERY TASK!
  response = render(request, 'order/build_voxel_world/html/make_order_4.html', 
                   {'origin':scene.origin,
                    'image_list':image_list,
                    'task_id': t.task_id})
  response.delete_cookie('order_build_voxel_world_uuid')

  return response

def order_status(request, task_id):
  import urllib2, json, os
  from celery.result import AsyncResult
  
  task = AsyncResult(task_id);
  
  status = {'task': task};
 
  return render(request, 'order/build_voxel_world/html/order_status.html',
                status)
  #return HttpResponse('Task %s\n%s' % (task_id, status))
