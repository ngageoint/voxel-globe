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
  payload_type = models.CharField(max_length=30)
  metadata_type = models.CharField(max_length=30)

class File(IngestCommonModel):
  session = models.ForeignKey('UploadSession', related_name='file');
  completed = models.BooleanField(default=False);
