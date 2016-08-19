from django.db import models
from django.contrib.auth.models import User

class LogMessage(models.Model):
  LOG_TYPE = (('d', 'Debug'), ('i', 'Info'), ('w', 'Warn'), 
    ('e', 'Error'), ('f', 'Fatal'), ('m', 'Message'))
  message_text = models.TextField()
  message_type = models.CharField(max_length=1, choices=LOG_TYPE)
  task_id = models.IntegerField()
  timestamp = models.DateTimeField(auto_now_add=True)
  owner = models.ForeignKey(User, null=True, blank=True, related_name="websockets_log_message_owner")
  read = models.BooleanField(default=False)

  def __unicode__(self):
    return self.message_text