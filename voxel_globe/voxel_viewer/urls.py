from django.conf.urls import patterns, url

# Create your urls here.

import voxel_globe.voxel_viewer.views as views

urlpatterns = patterns('',
    url(r'^displayVoxelWorld/$', views.display_voxel_world, name='display_voxel_world'),
    url(r'^fetchPointCloud$', views.fetch_point_cloud,  name='fetch_point_cloud'),
    )
