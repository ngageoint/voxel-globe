from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__);

@shared_task(base=VipTask, bind=True)
def krt(self, upload_session_id, image_dir):
  import voxel_globe.ingest.models as models

  upload_session = models.UploadSession.objects.get(id=upload_session_id)


krt.dbname = 'krt'
krt.description = 'VXL KRT perspective cameras'
krt.metadata_ingest=True