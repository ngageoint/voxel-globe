from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@shared_task(base=VipTask, bind=True)
def move_data(self, from_dir, to_dir):
  ''' All the logic for moving ingested data to the image server.

      Currently this is just a mv, but it may be a more complicated push in the
      future.'''

  import distutils.dir_util
  distutils.dir_util.copy_tree(from_dir, to_dir)
  distutils.dir_util.remove_tree(from_dir)

@shared_task(base=VipTask, bind=True)
def cleanup(self, upload_session_id):
  ''' Clean up after successful ingest 

      Currently this only entails removing the upload session information '''

  from voxel_globe.ingest.models import UploadSession
  upload_session = UploadSession.objects.get(id=upload_session_id)
  upload_session.delete()
