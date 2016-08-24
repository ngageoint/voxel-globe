from django.conf.urls import include, url

urlpatterns = [
  url(r'^ws/', include('voxel_globe.websockets.wsurls'))
]