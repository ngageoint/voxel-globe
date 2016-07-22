from django.conf.urls import patterns, url
import voxel_globe.event_trigger.views as views

urlpatterns = patterns('',
  url(r'^event_trigger_results$', views.event_trigger_results, name='event_trigger_results'),
  url(r'^create_event_trigger$', views.create_event_trigger, name='create_event_trigger'),
  url(r'^eventTriggerCreator/$', views.eventTriggerCreator, name='eventTriggerCreator'),
)