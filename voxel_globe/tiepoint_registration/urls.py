from django.conf.urls import url

# Create your urls here.

import voxel_globe.tiepoint_registration.views as views

urlpatterns = [
    url(r'^tiepoint_error$', views.tiepoint_error_1, name='tiepoint_error_1'),
    url(r'^tiepoint_error/(?P<image_set_id>\d+)$', views.tiepoint_error_2, name="tiepoint_error_2"),
    url(r'^tiepoint_error/(?P<image_set_id>\d+)/(?P<scene_id>\d+)$', views.tiepoint_error_3, name="tiepoint_error_3"),
    url(r'^status/(?P<task_id>\d+)$', views.order_status, name="order_status"),
    url(r'^tiepoint_registration$', views.tiepoint_registration_1, name='tiepoint_registration_1'),
    url(r'^tiepoint_registration/(?P<image_set_id>\d+)$', views.tiepoint_registration_2, name="tiepoint_registration_2"),
]