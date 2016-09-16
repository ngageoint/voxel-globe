from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.gis.geos import Point

from django.core import serializers
import voxel_globe.meta.models

import rest_framework.filters
import rest_framework.status
import rest_framework.response
import rest_framework.mixins
import rest_framework.views
import rest_framework.viewsets
import rest_framework.routers

import voxel_globe.meta.serializers

import inspect

### Django REST Framework setup ###

class AutoViewSet(rest_framework.mixins.CreateModelMixin,
                  rest_framework.mixins.RetrieveModelMixin,
                  rest_framework.mixins.UpdateModelMixin,
                  rest_framework.mixins.ListModelMixin,
                  rest_framework.mixins.DestroyModelMixin,
                  rest_framework.viewsets.GenericViewSet):
  filter_backends = (rest_framework.filters.DjangoFilterBackend,rest_framework.filters.OrderingFilter)

def ViewSetFactory(model, serializer):
  return type('AutoViewSet_%s' % model._meta.model_name, 
              (AutoViewSet,), 
              {'queryset':model.objects.all(), 
               'serializer_class':serializer,
               'ordering_fields':'__all__',
               'filter_fields': [f.name for f in model._meta.get_fields()
                                          if (not f.is_relation or f.one_to_one
                                              or (f.many_to_one 
                                                  and f.related_model)) and 
                                             f.model != model]})
               #https://github.com/django/django/blob/master/docs/ref/models/meta.txt

service_instance = voxel_globe.meta.models.ServiceInstance
ServiceInstanceViewSet = ViewSetFactory(service_instance, voxel_globe.meta.serializers.serializerFactory(service_instance))
ServiceInstanceViewSet.get_queryset = lambda self: super(ServiceInstanceViewSet, self).get_queryset().filter(user=self.request.user)

#Define custom view sets here

auto_router = rest_framework.routers.DefaultRouter()
router = rest_framework.routers.DefaultRouter()
router.register(r'serviceinstance', ServiceInstanceViewSet)
#router.register('tiepoint', TiePointViewSet)
#Register custom views/viewsets here
#May need to add if to for loop to check if already registered

''' Create serializers for all VIP object models '''
for m in inspect.getmembers(voxel_globe.meta.models):
  if inspect.isclass(m[1]):
    if issubclass(m[1], voxel_globe.meta.models.VipObjectModel) and not m[1] == voxel_globe.meta.models.VipObjectModel or m[1] == voxel_globe.meta.models.ServiceInstance:
      auto_router.register(m[1]._meta.model_name, ViewSetFactory(m[1], voxel_globe.meta.serializers.serializerFactory(m[1])))

### Old Archaic getters/setters, TODO: Remove EVERYTHING after this line
      
#
# API for grabbing data in the database
#
    
def fetchTiePoints(request):
  imageId = request.GET["imageId"]
  tiePoints = voxel_globe.meta.models.TiePoint.objects.filter(image_id=imageId)
  serializers.serialize('geojson', tiePoints, fields=('name', 'point', 'control_point'))
  return HttpResponse( serializers.serialize('geojson', tiePoints, fields=('name', 'point', 'control_point')) , content_type="application/json")
     
#  API for updating data in the database
def createTiePoint(request):
    import voxel_globe.tiepoint.tasks

    imageId = request.GET["imageId"]
    if 'controlPointId' in request.GET:
      controlPointId = request.GET["controlPointId"]
    else:
      controlPointId = None
    x = float(request.GET["x"])
    y = float(request.GET["y"])
    name = request.GET["name"]
    voxel_globe.tiepoint.tasks.addTiePoint.apply(
        kwargs={'x':x, 'y':y, 'image_id':imageId, 
                'control_point_id':controlPointId, 'name': name})
    return HttpResponse('')

def updateTiePoint(request):
    tp = voxel_globe.meta.models.TiePoint.objects.filter(
        id=request.GET["tiePointId"])
    tp.update(point = Point(float(request.GET["x"]),float(request.GET["y"])))
    #Eventually when the REAL update function is written, it may be EASIEST to say
    #"POINT(%s %s)" % (x, y), but until this is complete, it does not matter to me.

    return HttpResponse('')

def deleteTiePoint(request):
  tiePointId = request.REQUEST['id']
  voxel_globe.meta.models.TiePoint.objects.get(id=tiePointId).delete()
  return HttpResponse('')

def fetch_voxel_world_bounding_box(request, voxel_world_id):
  import boxm2_scene_adaptor
  import json
  import os

  voxel_world = voxel_globe.meta.models.VoxelWorld.objects.get(
      id=voxel_world_id)

  scene = boxm2_scene_adaptor.boxm2_scene_adaptor(
      os.path.join(voxel_world.directory, 'scene.xml'), 'cpp')

  return HttpResponse(json.dumps(scene.bbox), content_type="application/json")

def get_additional_image_info(request, image_id, camera_set_id):
  import json

  response = {}

  image = voxel_globe.meta.models.Image.objects.get(id=image_id)

  rpc = image.camera_set.filter(cameraset=camera_set_id).select_subclasses('rpccamera')[0]
  if type(rpc) != voxel_globe.meta.models.RpcCamera:
    rpc = None

  #Same for perspective here

  attributes = image.attributes
  if attributes.has_key("planet_rest_response"):
    response['gsd'] = attributes['planet_rest_response']['properties']['image_statistics']['gsd']
  else:
    pass #Check for RPC or perspective camera, and get gsd

  if rpc:
    import brl_init
    import vpgl_adaptor_boxm2_batch as vpgl
    print 0
    vxl_cam =vpgl.load_rational_camera_from_txt(rpc.rpc_path)
    print 1, vxl_cam
    print vpgl.rational_camera_rotate_to_north(vxl_cam)
    print 2
    response['north_rotation'] = vpgl.rational_camera_rotate_to_north(vxl_cam)
  response['up_rotation'] = 1.1

  return HttpResponse(json.dumps(response), content_type="application/json")