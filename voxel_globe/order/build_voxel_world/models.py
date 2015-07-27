from django.db import models

class Session(models.Model):
  owner = models.ForeignKey('auth.user', null=False, blank=False, related_name="order_build_voxel_world_session_owner");
  uuid = models.CharField(max_length=36, null=False, blank=False);
  startTime = models.DateTimeField(auto_now_add = True);