from django.conf.urls import patterns, url
import voxel_globe.event_trigger.views as views

urlpatterns = patterns('',
  url(r'^event_trigger_results$', views.event_trigger_results, name='event_trigger_results'),
  url(r'^create_event_trigger$', views.create_event_trigger, name='create_event_trigger'),
  url(r'^update_geometry_polygon $', views.update_geometry_polygon , name='update_geometry_polygon '),
  url(r'^get_event_geometry$', views.get_event_geometry, name='get_event_geometry'),
  url(r'^run_event_trigger$', views.run_event_trigger, name='run_event_trigger'),
  url(r'^eventTriggerCreator/$', views.eventTriggerCreator, name='eventTriggerCreator'),
)