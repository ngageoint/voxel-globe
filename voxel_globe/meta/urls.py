from django.conf.urls import patterns, url, include
from voxel_globe.meta import views

urlpatterns = patterns('',
# json API calls    
    url(r'^fetchTiePoints$', views.fetchTiePoints, name='fetchTiePoints'),
    
#   modifications to data
    url(r'^createTiePoint$', views.createTiePoint, name='createTiePoint'),
    url(r'^updateTiePoint$', views.updateTiePoint, name='updateTiePoint'),
    url(r'^deleteTiePoint$', views.deleteTiePoint, name='deleteTiePoint'),

#   RESTful end points
    url(r'^rest/', include(views.router.urls)),
    url(r'^rest/auto/', include(views.auto_router.urls)),
)