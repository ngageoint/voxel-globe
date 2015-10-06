import distutils.dir_util
import os


from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext


### Rest API setup
import rest_framework.routers
import rest_framework.viewsets
import rest_framework.filters
import voxel_globe.ingest.serializers


from .tools import METADATA_TYPES, PAYLOAD_TYPES
#Deprecating ...
from .tools import SENSOR_TYPES

from voxel_globe.ingest import models


router = rest_framework.routers.DefaultRouter()


class IngestViewSet(rest_framework.viewsets.ModelViewSet):
  filter_backends = (rest_framework.filters.DjangoFilterBackend,);
  filter_fields = ['id', 'name']#, 'directory', 'file'];
  def perform_create(self, serializer):
    serializer.save(owner=self.request.user)
    super(IngestViewSet, self).perform_create(serializer);
  def get_queryset(self):
    return super(IngestViewSet, self).get_queryset().filter(owner=self.request.user);
  
def ViewSetFactory(model, serializer):
  return type('ViewSet_%s' % model._meta.model_name, (IngestViewSet,), {'queryset':model.objects.all(), 'serializer_class':serializer})

router.register(models.File._meta.model_name, ViewSetFactory(models.File, voxel_globe.ingest.serializers.FileSerializer))
#router.register(models.Directory._meta.model_name, ViewSetFactory(models.Directory, voxel_globe.ingest.serializers.DirectorySerializer))
#router.register(models.Directory._meta.model_name+'_nest', ViewSetFactory(models.Directory, voxel_globe.ingest.serializers.NestFactory(voxel_globe.ingest.serializers.DirectorySerializer)))
router.register(models.UploadSession._meta.model_name, ViewSetFactory(models.UploadSession, voxel_globe.ingest.serializers.UploadSessionSerializer));
#router.register(models.UploadSession._meta.model_name+'_nest', ViewSetFactory(models.UploadSession, voxel_globe.ingest.serializers.NestFactory(voxel_globe.ingest.serializers.UploadSessionSerializer)));

def chooseSession(request):
    return render_to_response('ingest/html/chooseSession.html', 
                            {'sensorTypes': SENSOR_TYPES,
                             'payload_types': PAYLOAD_TYPES,
                             'metadata_types': METADATA_TYPES}, 
                            context_instance=RequestContext(request))

def addFiles(request):
  upload_session_id = int(request.GET['upload'])
  uploadSession = models.UploadSession.objects.get(id=upload_session_id)
  
  testFile = models.File(name='Newfile', session=uploadSession, owner=request.user);
  testFile.save();

  return render_to_response('ingest/html/addFiles.html',
                           {'uploadSession':uploadSession,
                            'testFile':testFile}, 
                            context_instance=RequestContext(request))

  
def upload(request):
  try:
    uploadSession_id = request.POST['uploadSession']
  except:
    uploadSession = models.UploadSession(name='failesafe', owner=request.user)
    uploadSession.save();
    uploadSession.name = str(uploadSession.id); uploadSession.save();
    uploadSession_id = uploadSession.id

  try:
    testFile_id = request.POST['testFile']
  except:
    testFile_id = 'failsafe'

  s = 'ok<br>'
  
  saveDir = os.path.join(os.environ['VIP_TEMP_DIR'], 'ingest', str(uploadSession_id))
  distutils.dir_util.mkpath(saveDir)
  
  for f in request.FILES:
    s += request.FILES[f].name
    with open(os.path.join(saveDir, request.FILES[f].name), 'wb') as fid:
      for c in request.FILES[f].chunks():
        fid.write(c)
  
  return HttpResponse(s);

def ingestFolder(request):
  from vsi.tools.dir_util import mkdtemp
  from celery.canvas import chain

  uploadSession_id = request.POST['uploadSession']
  #directories = models.Directory.objects.filter(uploadSession_id = uploadSession_id)
  #Code not quite done, using failsafe for now. 
  uploadSession = models.UploadSession.objects.get(id=uploadSession_id);

  sessionDir = os.path.join(os.environ['VIP_TEMP_DIR'], 'ingest', str(uploadSession.id))
  #imageDir = os.path.join(os.environ['VIP_IMAGE_SERVER_ROOT'], str(uploadSession.id))
  #if os.path.exists(imageDir):
  imageDir = mkdtemp(dir=os.environ['VIP_IMAGE_SERVER_ROOT'], prefix='img');
  
  #Deprecated code
  if uploadSession.sensorType != "None":
    distutils.dir_util.copy_tree(sessionDir, imageDir)
    distutils.dir_util.remove_tree(sessionDir)
    task = SENSOR_TYPES[uploadSession.sensorType].ingest_data.delay(uploadSession_id, imageDir)
    result=task
  else:
    #This is the REAL non-deprecated code. Not done yet ;)
    import voxel_globe.ingest.tasks
    task0 = voxel_globe.ingest.tasks.move_data.si(sessionDir, imageDir)
    task1 = PAYLOAD_TYPES[uploadSession.payload_type].ingest.si(uploadSession_id, imageDir)
    task2 = METADATA_TYPES[uploadSession.metadata_type].ingest.s(uploadSession_id, imageDir)
    task3 = voxel_globe.ingest.tasks.cleanup.si(uploadSession_id)
    tasks = task0 | task1 | task2 | task3 #create chain
    result = tasks.apply_async()

  return render(request, 'ingest/html/ingest_started.html', 
                {'task_id':result.task_id})
