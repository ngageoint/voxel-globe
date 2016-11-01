import os
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy

def validate_file(value):
  return os.path.isfile(os.path.expandvars(value)) or \
         os.path.isdir(os.path.expandvars(value))

class FileNameField(models.TextField):
  #Field for a file or directory
  default_validators = [validate_file]
  description = ugettext_lazy("File Name")
  
  def __init__(self, *args, **kwargs):
    self.path = kwargs.pop('path', None)
    super(FileNameField, self).__init__(*args, **kwargs)
  
  def check(self, *args, **kwargs):
    errors = super(FileNameField, self).check(*args, **kwargs)
    errors.extend(self._check_path_attribute(*args, **kwargs))
    return errors

  def _check_path_attribute(self, **kwargs):
    if self.path is None:
      return [checks.Error("FileNameField must define a 'path' attribute.",
                           obj=self, id='voxel_globe.E1')]
    else:
      return []
    
  def deconstruct(self):
    name, path, args, kwargs = super(FilePathField, self).deconstruct()
    kwargs['path'] = self.path
    return name, path, args, kwargs
    
