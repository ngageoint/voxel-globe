import os
import shutil
import django.apps.apps
from voxel_globe.meta.fields import FileNameField
from django.db.models.signals import post_delete
from vsi.tools.dir_util import is_subdir, prune_dir
import logging
logger = logging.getLogger(__name__)

#simplified https://github.com/un1t/django-cleanup/
def prepare():
  for model in django.apps.apps.get_models():
    for field in model._meta.get_fields():
      if field.concrete and 
         not field.is_related_model and
         isinstance(field, FileNameField):
        post_delete.connect(delete_file_post_delete, sender=model,
            dispatch_uid='{mm.app_label}_{mm.model_name}_post_delete'.format(
                mm=model._meta))
        break

def delete_file_post_delete(sender, instance, using, **kwargs):
  for field in instance._meta.get_fields():
    if isinstance(field, FileNameField):
      filename = os.path.expandvars(getattr(instance, field.name))
      if is_subdir(filename, path):
        if os.path.isfile(filename):
          os.remove(filename)
          prune_dir(os.path.dirname(filename))
        elif os.path.isdir(filename):
          shutil.rmtree(filename)
          prune_dir(filename)
        else:
          logger.error('Deletion of a non-existing file attempted: {}'.format(
              filename))
      else:
        logger.warning('Deletion outside of {} attempted: {}'.format(path, 
                                                                     filename))


