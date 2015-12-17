from django.db import models

# Create your models here.

class Session(models.Model):
  owner = models.ForeignKey('auth.user', null=False, blank=False, related_name="session_owner");
  uuid = models.CharField(max_length=36, null=False, blank=False)
  #major_step = models.IntegerField()
  #minor_step = models.IntegerField()
  startTime = models.DateTimeField(auto_now_add = True)