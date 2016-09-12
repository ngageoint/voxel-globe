from django.conf.urls import patterns, url

# Create your urls here.

import voxel_globe.generate_point_cloud.views as views

urlpatterns = patterns('',
    url(r'^threshold_pointcloud$', views.threshold_pointcloud_1, name='threshold_pointcloud_1'),
    url(r'^threshold_pointcloud/(?P<voxel_world_id>\d+)$', views.threshold_pointcloud_2, name="threshold_pointcloud_2"),
    url(r'^threshold_pointcloud/(?P<voxel_world_id>\d+)/order$', views.threshold_pointcloud_3, name="threshold_pointcloud_3"),
    url(r'^error_pointcloud$', views.error_pointcloud, name='error_pointcloud'),
)
