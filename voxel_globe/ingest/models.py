from django.db import models

# Create your models here.

class IngestCommonModel(models.Model):
  class Meta:
    abstract = True
  name = models.TextField();
  owner = models.ForeignKey('auth.user');

  def __unicode__(self):
    return '%s[%s]: %s' % (self.name, self.id, self.owner.username)

class UploadSession(IngestCommonModel):
  sensorType = models.CharField(max_length=30)
  pass

class Directory(IngestCommonModel):
  session = models.ForeignKey('UploadSession', related_name='directory');

class File(IngestCommonModel):
  directory = models.ForeignKey('Directory', related_name='file');
  completed = models.BooleanField(default=False);
