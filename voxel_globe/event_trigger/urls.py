from django.conf.urls import patterns, url
import voxel_globe.event_trigger.views as views

urlpatterns = patterns('',
  url(r'^$', views.event_trigger, name='event_trigger')
  url(r'^eventTriggerCreator/$', views.eventTriggerCreator, name='eventTriggerCreator'),
)