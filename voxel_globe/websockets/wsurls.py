from django.conf.urls import include, url

from .views import 

urlpatterns = [
  url(r'^logger/(?P<user_id>\d+)/(?P<session_key>[a-z0-9]+)$', , name='get_additional_image_info'),
  #session pattern is based off of django.contrib.sessions.backends.base.VALID_KEY_CHARS
]