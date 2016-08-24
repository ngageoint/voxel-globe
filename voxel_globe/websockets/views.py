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

class WebSocket(object):
  def connect(message):
    pass
  def message(message):
    pass
  def disconnect(message):
    pass

class LogSocket(object):
  def connect(message, user_id, session):
    user_id = user_id
    session = session
    message.channel_session['user_id'] = user_id
    message.channel_session['session_key'] = session

    if user_id != message.user.id:
      raise ValueError("That's not you! %d : %d" % (user_id, message.user.id))
      return
    if session != message.http_session.session_key:
      raise ValueError("That's not your session! %s : %s" % (session, message.http_session.session_key))
      return

    Group("ws_logger_%d" % user_id).add(message.reply_channel)

  def message(message):
    pass

  def disconnect(message):
    pass