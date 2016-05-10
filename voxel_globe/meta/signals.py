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

    if instance.filename and os.path.exists(instance.filename):
      os.remove(instance.filename)
      try:
        os.rmdir(os.path.dirname(instance.filename))
      except:
        pass

      try:
        if instance.potree_url:
          potree_dir = instance.potree_url.split('/images/', 1)[1]
          potree_dir = os.path.join(os.environ['VIP_IMAGE_SERVER_ROOT'], potree_dir)
          potree_dir = os.path.dirname(potree_dir)
          shutil.rmtree(potree_dir)
      except:
        pass
