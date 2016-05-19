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

from .tools import CONTROLPOINT_TYPES

from voxel_globe.ingest import models


router = rest_framework.routers.DefaultRouter()

#TODO: Pass upload types, then all the upload type types
#New a new "New session" panel to handle adding all sorts of upload types
def chooseSession(request):
  return render_to_response('ingest_controlpoint/html/chooseSession.html', 
                            {'controlpoint_types': CONTROLPOINT_TYPES}, 
                            context_instance=RequestContext(request))

def addFiles(request):
  upload_session_id = int(request.GET['upload'])
  uploadSession = models.UploadSession.objects.get(id=upload_session_id)
  
  testFile = models.File(name='Newfile', session=uploadSession, owner=request.user)
  testFile.save()

  return render_to_response('ingest_controlpoint/html/addFiles.html',
                           {'uploadSession':uploadSession,
                            'testFile':testFile}, 
                            context_instance=RequestContext(request))

  
def upload(request):
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

def ingestFolder(request):
  import json

  from celery.canvas import chain

  from vsi.tools.dir_util import mkdtemp

  import voxel_globe.ingest.tasks

  uploadSession_id = request.POST['uploadSession']
  #directories = models.Directory.objects.filter(uploadSession_id = uploadSession_id)
  #Code not quite done, using failsafe for now. 
  uploadSession = models.UploadSession.objects.get(id=uploadSession_id)

  upload_types = json.loads(uploadSession.upload_types)
  controlpoint_type = upload_types['controlpoint_type']

  sessionDir = os.path.join(os.environ['VIP_TEMP_DIR'], 'ingest_controlpoint', str(uploadSession.id))

  task1 = CONTROLPOINT_TYPES[controlpoint_type].ingest.si(uploadSession_id, sessionDir)
  task3 = voxel_globe.ingest.tasks.cleanup.si(uploadSession_id)
  tasks = task1 | task3 #create chain
  result = tasks.apply_async()

  return render(request, 'ingest_controlpoint/html/ingest_started.html', 
                {'task_id':result.task_id})
