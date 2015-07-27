from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

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
                  rest_framework.viewsets.GenericViewSet):
  filter_backends = (rest_framework.filters.DjangoFilterBackend,);
  
  def destroy(self, request, pk=None, *args, **kwargs):
    ''' Destroy that sets delete to true, but does not actually delete to support history'''
    try:
      obj = self.get_queryset().get(pk=pk).history();
      #obj = voxel_globe.meta.models.TiePoint.objects.get(id=tiePointId).history();
      #Get the latest version of that tiepoint
      obj.deleted = True;
      super(obj._meta.model, obj).save();
      #Do not use the VIPModel save, since this is a strict change in a status flag
      return rest_framework.response.Response(status=rest_framework.status.HTTP_204_NO_CONTENT)
    except:
      #pk may have been None, or obj may have been None.
      return rest_framework.response.Response(status=rest_framework.status.HTTP_400_BAD_REQUEST);

  def get_queryset(self):
    ''' Get Queryset that supports "newestVersion" as a PARAM to newerVerion==None '''
    if self.request.QUERY_PARAMS.has_key('newestVersion'):
      return super(AutoViewSet, self).get_queryset().filter(newerVersion=None);
    else:
      return super(AutoViewSet, self).get_queryset();

#  def list(self, request):
#    print 'LIST';
#    #Called by main endpoint GET, to list (a page if) the objects

#  def retrieve(self, request, pk=None):
#    print 'RETREIVE';
#    #Called by the individual id endpoint GET
  
#  def create(self, request):
#    print 'CREATE';
#    Called by main endpoint POST

#  def update(self, request, pk=None):
#    print 'UPDATE';
#    #Individual id endpoint PUT
    
#  def partial_update(self, request, pk=None):
#    print 'PARTIAL_UPDATE'
#    #Individual id endpoint PATCH


def ViewSetFactory(model, serilizer):
  return type('AutoViewSet_%s' % model._meta.model_name, 
              (AutoViewSet,), 
              {'queryset':model.objects.all(), 
               'serializer_class':serilizer,
               'filter_fields': map(lambda x: x[0].name, model._meta.get_fields_with_model())})
  

#Define custom view sets here

auto_router = rest_framework.routers.DefaultRouter()
router = rest_framework.routers.DefaultRouter()
#router.register('tiepoint', TiePointViewSet);
#Register custom views/viewsets here
#May need to add if to for loop to check if already registered

''' Create serializers for all VIP object models '''
for m in inspect.getmembers(voxel_globe.meta.models):
  if inspect.isclass(m[1]):
    if issubclass(m[1], voxel_globe.meta.models.VipObjectModel) and not m[1] == voxel_globe.meta.models.VipObjectModel:
      #pass
      auto_router.register(m[1]._meta.model_name, ViewSetFactory(m[1], voxel_globe.meta.serializers.serializerFactory(m[1])))
      

### Old Arcaic getters/setters, TODO: Remove EVERYTHING after this line
      
#
# API for grabbing data in the database
#
def fetchVideoList(request):
    imgs = voxel_globe.meta.models.ImageCollection.objects.all()
    return HttpResponse( serializers.serialize('geojson', imgs) , content_type="application/json")

def fetchImages(request):
  try:
    videoId = request.REQUEST["videoId"]
    video = voxel_globe.meta.models.ImageCollection.objects.get(id=videoId)
#    return HttpResponse( serializers.serialize('geojson', video.images.all(), fields=('name',)), 
#                         content_type="application/json")
    return HttpResponse( serializers.serialize('geojson', video.images.all()), 
                         content_type="application/json")
    #based off of video_list_example.ipynb
  except voxel_globe.meta.models.ImageCollection.DoesNotExist:
    return HttpResponse('')
    
def fetchControlPointList(request):    
    geoPoints = voxel_globe.meta.models.ControlPoint.objects.all()    
    return HttpResponse( serializers.serialize('geojson', geoPoints) , content_type="application/json")
  
def fetchTiePoints(request):
  imageId = request.REQUEST["imageId"]
  tiePoints = voxel_globe.meta.models.TiePoint.objects.filter(image_id=imageId, newerVersion=None, deleted=False)
  serializers.serialize('geojson', tiePoints, fields=('name', 'point', 'geoPoint'))
  return HttpResponse( serializers.serialize('geojson', tiePoints, fields=('name', 'point', 'geoPoint')) , content_type="application/json")
     
#  API for updating data in the database
def createTiePoint(request):
    import voxel_globe.tiepoint.tasks

    imageId = request.REQUEST["imageId"];
    if 'controlPointId' in request.REQUEST:
      controlPointId = request.REQUEST["controlPointId"];
    else:
      controlPointId = None;
    x = request.REQUEST["x"];
    y = request.REQUEST["y"];
    name = request.REQUEST["name"];
    voxel_globe.tiepoint.tasks.addTiePoint.apply(kwargs={'point':'POINT(%s %s)' % (x,y), 
                                    'image_id':imageId, 
                                    'geoPoint_id':controlPointId,
                                    'name': name});
    return HttpResponse('');

def updateTiePoint(request):
    import voxel_globe.tiepoint.tasks

    print("Requested to update a tie point with id ", request.REQUEST["tiePointId"],           
          " with x=", request.REQUEST["x"], " and y=", request.REQUEST["y"])    

    voxel_globe.tiepoint.tasks.updateTiePoint.apply(args=(request.REQUEST["tiePointId"], request.REQUEST["x"], request.REQUEST["y"]))
    #Eventually when the REAL update function is written, it may be EASIEST to say
    #"POINT(%s %s)" % (x, y), but until this is complete, it does not matter to me.
          
    return HttpResponse('');

def deleteTiePoint(request):
  tiePointId = request.REQUEST['id']
  object = voxel_globe.meta.models.TiePoint.objects.get(id=tiePointId).history();
  #Get the latest version of that tiepoint
  object.deleted = True;
  super(object._meta.model, object).save();
  #Do not use the VIPModel save, since this is a strict change in a status flag
  return HttpResponse('');
