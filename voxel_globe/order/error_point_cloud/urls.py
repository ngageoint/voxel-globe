from django.conf.urls import patterns, url

# Create your urls here.

import voxel_globe.order.error_point_cloud.views as views

urlpatterns = patterns('',
    url(r'^$', views.make_order, name='make_order'),
    url(r'^$', views.make_order_1, name='make_order_1'),
    url(r'^order/(?P<voxel_world_id>\d+)$', views.make_order_2, name="make_order_2"),
    url(r'^order/(?P<voxel_world_id>\d+)/order$', views.make_order_3, name="make_order_3")
    )
