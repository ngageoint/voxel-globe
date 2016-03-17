from django.conf.urls import patterns, url, include
from voxel_globe.meta import views

urlpatterns = patterns('',
# json API calls    
    url(r'^fetchTiePoints$', views.fetchTiePoints, name='fetchTiePoints'),
    url(r'^fetch_voxel_world_bbox/(?P<voxel_world_id>\d+)$', views.fetch_voxel_world_bounding_box, name='fetch_voxel_world_bbox'),
    
#   modifications to data
    url(r'^createTiePoint$', views.createTiePoint, name='createTiePoint'),
    url(r'^updateTiePoint$', views.updateTiePoint, name='updateTiePoint'),
    url(r'^deleteTiePoint$', views.deleteTiePoint, name='deleteTiePoint'),

#   RESTful end points
    url(r'^rest/', include(views.router.urls)),
    url(r'^rest/auto/', include(views.auto_router.urls)),
)