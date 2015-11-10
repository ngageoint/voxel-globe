from django.conf.urls import patterns, url

# Create your urls here.

import voxel_globe.order.point_cloud.views as views

urlpatterns = patterns('',
    url(r'^$', views.make_order_1, name='make_order_1'),
    url(r'^order/(?P<voxel_world_id>\d+)$', views.make_order_2, name="make_order_2")
    )
