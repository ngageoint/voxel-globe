from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__);

# @shared_task(base=VipTask, bind=True)
# def ingest(self, upload_session_id, image_dir):
#   import voxel_globe.ingest.models as models

#   upload_session = models.UploadSession.objects.get(id=upload_session_id)

#   #Deprecated remove when everything converted to new way
#   old_type = upload_session.sensorType #not going to PEP8 sensorType, del it
#   if old_type != "None":
    
#     return

@shared_task(base=VipTask, bind=True)
def move_data(self, from_dir, to_dir):
  import distutils.dir_util
  distutils.dir_util.copy_tree(from_dir, to_dir)
  distutils.dir_util.remove_tree(from_dir)
