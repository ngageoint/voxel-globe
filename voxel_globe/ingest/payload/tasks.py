from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__);

@shared_task(base=VipTask, bind=True)
def images(self, upload_session_id, image_dir):
  import voxel_globe.ingest.models as models

  upload_session = models.UploadSession.objects.get(id=upload_session_id)


images.dbname = 'images'
images.description = 'Image Sequence'
images.payload_ingest=True