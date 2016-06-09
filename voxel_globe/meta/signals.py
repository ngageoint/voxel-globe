import django.dispatch
import django.db.models.signals as db_signals
import models
from django.dispatch import receiver

@receiver(db_signals.pre_delete, sender=models.PointCloud)
def point_cloud_pre_delete(sender, **kwargs):
  import os
  import shutil

  if 'instance' in kwargs:
    instance = kwargs['instance']

    if instance.filename_path and os.path.exists(instance.filename_path):
      os.remove(instance.filename_path)
      try:
        os.rmdir(os.path.dirname(instance.filename_path))
      except:
        pass

      try:
        shutil.rmtree(instance.potree_dir)
      except:
        pass
