from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@shared_task(base=VipTask, bind=True)
def cleanup(self, upload_session_id):
  ''' Clean up after successful ingest 

      Currently this only entails removing the upload session information '''

  from voxel_globe.ingest.models import UploadSession
  upload_session = UploadSession.objects.get(id=upload_session_id)
  upload_session.delete()
