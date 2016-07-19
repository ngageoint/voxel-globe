from django.conf.urls import patterns, url, include
from voxel_globe.event_trigger import views

urlpatterns = patterns('',
# pages
  url(r'^eventTriggerCreator/$', views.eventTriggerCreator, name='eventTriggerCreator'),

)