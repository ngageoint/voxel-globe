from django.conf.urls import url, include
from voxel_globe.meta import views

urlpatterns = [
# json API calls    
    url(r'^fetchTiePoints$', views.fetchTiePoints, name='fetchTiePoints'),
    url(r'^fetch_voxel_world_bbox/(?P<voxel_world_id>\d+)$', views.fetch_voxel_world_bounding_box, name='fetch_voxel_world_bbox'),

    url(r'^get_additional_image_info/(?P<image_id>\d+)/(?P<camera_set_id>\d+)$', views.get_additional_image_info, name='get_additional_image_info'),

    
#   modifications to data
    url(r'^createTiePoint$', views.createTiePoint, name='createTiePoint'),
    url(r'^updateTiePoint$', views.updateTiePoint, name='updateTiePoint'),
    url(r'^deleteTiePoint$', views.deleteTiePoint, name='deleteTiePoint'),

#   RESTful end points
    url(r'^rest/', include(views.router.urls)),
    url(r'^rest/auto/', include(views.auto_router.urls)),
]