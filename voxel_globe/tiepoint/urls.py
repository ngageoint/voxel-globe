from django.conf.urls import patterns, url, include
from voxel_globe.tiepoint import views

urlpatterns = patterns('',
# pages
  url(r'^tiePointCreator/$', views.tiePointCreator, name='tiePointCreator'),
  url(r'^fetchCameraRay$', views.fetchCameraRay, name='fetchCameraRay'),
  url(r'^fetchCameraFrustum$', views.fetchCameraFrustum, name='fetchCameraFrustum'),

)