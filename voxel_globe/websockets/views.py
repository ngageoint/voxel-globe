from django.shortcuts import render

### Rest API setup
import rest_framework.routers
import rest_framework.viewsets
import rest_framework.filters
from voxel_globe.websockets.serializers import LogMessageSerializer
from voxel_globe.websockets.models import LogMessage

router = rest_framework.routers.DefaultRouter()

class LogMessageViewSet(rest_framework.viewsets.ModelViewSet):
  queryset = LogMessage.objects.all()
  serializer_class = LogMessageSerializer
  filter_backends = (rest_framework.filters.DjangoFilterBackend,)
  filter_fields = ['message_text', 'message_type', 'task_id']

  def get_queryset(self):
    return super(LogMessageViewSet, self).get_queryset().filter(owner=self.request.user)
