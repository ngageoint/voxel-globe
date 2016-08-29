from django.conf.urls import patterns, url
import voxel_globe.security.views as views

urlpatterns = patterns('',
    url(r'', views.images, name='images'),
)