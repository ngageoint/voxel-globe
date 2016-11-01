from rest_framework import serializers
from voxel_globe.websockets.models import LogMessage

class LogMessageSerializer(serializers.ModelSerializer):
  message_type = serializers.CharField(source='get_message_type_display')
  class Meta:
    model = LogMessage
    fields = ('message_text', 'message_type', 'task_id', 'timestamp', 'owner', 'read', 'id')