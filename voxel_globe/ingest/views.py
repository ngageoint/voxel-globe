import distutils.dir_util
import os


from django.shortcuts import render
from django.http import HttpResponse


### Rest API setup
import rest_framework.routers
import rest_framework.viewsets
import rest_framework.filters
import voxel_globe.ingest.serializers

from .tools import ControlPointTypes

from voxel_globe.ingest import models


router = rest_framework.routers.DefaultRouter()


class IngestViewSet(rest_framework.viewsets.ModelViewSet):
  filter_backends = (rest_framework.filters.DjangoFilterBackend,)
  filter_fields = ['id', 'name']#, 'directory', 'file']
  def perform_create(self, serializer):
    serializer.save(owner=self.request.user)
    super(IngestViewSet, self).perform_create(serializer)
  def get_queryset(self):
    return super(IngestViewSet, self).get_queryset().filter(owner=self.request.user)
  
def ViewSetFactory(model, serializer):
  return type('ViewSet_%s' % model._meta.model_name, (IngestViewSet,), {'queryset':model.objects.all(), 'serializer_class':serializer})

router.register(models.File._meta.model_name, ViewSetFactory(models.File, voxel_globe.ingest.serializers.FileSerializer))
#router.register(models.Directory._meta.model_name, ViewSetFactory(models.Directory, voxel_globe.ingest.serializers.DirectorySerializer))
#router.register(models.Directory._meta.model_name+'_nest', ViewSetFactory(models.Directory, voxel_globe.ingest.serializers.NestFactory(voxel_globe.ingest.serializers.DirectorySerializer)))
router.register(models.UploadSession._meta.model_name, ViewSetFactory(models.UploadSession, voxel_globe.ingest.serializers.UploadSessionSerializer))
#router.register(models.UploadSession._meta.model_name+'_nest', ViewSetFactory(models.UploadSession, voxel_globe.ingest.serializers.NestFactory(voxel_globe.ingest.serializers.UploadSessionSerializer)))

#TODO: Pass upload types, then all the upload type types
#New a new "New session" panel to handle adding all sorts of upload types
def chooseSession(request):
  from .metadata.tasks import MetadataTypes
  from .payload.tasks import PayloadTypes
  from .controlpoint.tasks import ControlPointTypes

  return render(request, 'ingest/html/chooseSession.html', 
                        {'payload_types': PayloadTypes,
                         'metadata_types': MetadataTypes,
                         'controlpoint_types': ControlPointTypes})

def addFiles(request):
  upload_session_id = int(request.GET['upload'])
  uploadSession = models.UploadSession.objects.get(id=upload_session_id)
  
  testFile = models.File(name='Newfile', session=uploadSession, owner=request.user)
  testFile.save()

  return render(request, 'ingest/html/addFiles.html',
                        {'uploadSession':uploadSession,
                         'testFile':testFile})

  
def uploadImage(request):
  try:
    uploadSession_id = request.POST['uploadSession']
  except:
    uploadSession = models.UploadSession(name='failesafe', owner=request.user)
    uploadSession.save()
    uploadSession.name = str(uploadSession.id); uploadSession.save()
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
    # with open(os.path.join(saveDir, request.FILES[f].name), 'rb') as fid:
    #   print "Fid: " + fid.read()
  
  return HttpResponse(s)

def uploadControlpoint(request):
  try:
    uploadSession_id = request.POST['uploadSession']
  except:
    uploadSession = models.UploadSession(name='failesafe', owner=request.user)
    uploadSession.save()
    uploadSession.name = str(uploadSession.id); uploadSession.save()
    uploadSession_id = uploadSession.id

  s = 'ok<br>'
  
  saveDir = os.path.join(os.environ['VIP_TEMP_DIR'], 'ingest_controlpoint', str(uploadSession_id))
  distutils.dir_util.mkpath(saveDir)
  
  for f in request.FILES:
    s += request.FILES[f].name
    with open(os.path.join(saveDir, request.FILES[f].name), 'wb') as fid:
      for c in request.FILES[f].chunks():
        fid.write(c)
  
  return HttpResponse(s)

def ingestFolderImage(request):
  from celery.canvas import chain

  from vsi.tools.dir_util import mkdtemp

  import voxel_globe.ingest.tasks
  import voxel_globe.tools
  import distutils.dir_util

  from .metadata.tasks import MetadataTypes
  from .payload.tasks import PayloadTypes
  
  uploadSession_id = request.POST['uploadSession']
  #directories = models.Directory.objects.filter(uploadSession_id = uploadSession_id)
  #Code not quite done, using failsafe for now. 
  uploadSession = models.UploadSession.objects.get(id=uploadSession_id)
  # print 'Upload session id: '
  # print os.path.join(os.environ['VIP_TEMP_DIR'], 'ingest', str(uploadSession.id))

  sessionDir = os.path.join(os.environ['VIP_TEMP_DIR'], 'ingest', str(uploadSession.id))

  with voxel_globe.tools.storage_dir('ingest') as imageDir:
    #task0 = voxel_globe.ingest.tasks.move_data.si(sessionDir, imageDir)

    distutils.dir_util.copy_tree(sessionDir, imageDir)
    distutils.dir_util.remove_tree(sessionDir)

    # for dirpath, subdirs, files in os.walk(imageDir):
    #   for f in files:
    #     print f

    task1 = PayloadTypes[uploadSession.payload_type].ingest.si(uploadSession_id, imageDir)
    task2 = MetadataTypes[uploadSession.metadata_type].ingest.s(uploadSession_id, imageDir)
    task3 = voxel_globe.ingest.tasks.cleanup.si(uploadSession_id)
    tasks = task1 | task2 | task3 #create chain
    result = tasks.apply_async()

  return render(request, 'ingest/html/ingest_started.html', 
                {'task_id':result.task_id})

def ingestFolderControlpoint(request):
  import json

  from celery.canvas import chain

  from vsi.tools.dir_util import mkdtemp

  import voxel_globe.ingest.tasks

  from .controlpoint.tasks import ControlPointTypes

  uploadSession_id = request.POST['uploadSession']
  #directories = models.Directory.objects.filter(uploadSession_id = uploadSession_id)
  #Code not quite done, using failsafe for now. 
  uploadSession = models.UploadSession.objects.get(id=uploadSession_id)

  upload_types = json.loads(uploadSession.upload_types)
  controlpoint_type = upload_types['controlpoint_type']

  sessionDir = os.path.join(os.environ['VIP_TEMP_DIR'], 'ingest_controlpoint', str(uploadSession.id))

  with voxel_globe.tools.storage_dir('ingest_control_points') as data_dir:

    distutils.dir_util.copy_tree(sessionDir, data_dir)
    distutils.dir_util.remove_tree(sessionDir)

    task1 = ControlPointTypes[controlpoint_type].ingest.si(uploadSession_id, data_dir)
    task3 = voxel_globe.ingest.tasks.cleanup.si(uploadSession_id)
    tasks = task1 | task3 #create chain
    result = tasks.apply_async()

  return render(request, 'ingest/html/ingest_started.html', 
                {'task_id':result.task_id})
