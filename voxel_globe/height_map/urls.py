from django.conf.urls import patterns, url

# Create your urls here.

import voxel_globe.height_map.views as views

urlpatterns = patterns('',
    url(r'^dem_error$', views.calculate_dem_error, name='calculate_dem_error'),
    url(r'^height_map$', views.make_height_map, name='make_height_map'),
    url(r'^status/(?P<task_id>\d+)$', views.order_status, name="order_status"),
    )
