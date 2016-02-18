from django.conf.urls import patterns, url

# Create your urls here.

import voxel_globe.order.dem_error.views as views

urlpatterns = patterns('',
    url(r'^$', views.make_order, name='make_order'),
    url(r'^status/(?P<task_id>\d+)$', views.order_status, name="order_status"),
    )
