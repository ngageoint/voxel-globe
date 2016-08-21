from django.conf.urls import patterns, url
import voxel_globe.channel_test.views as views

urlpatterns = patterns('',
    url(r'^$', views.channel_test, name='channel_test')
    )