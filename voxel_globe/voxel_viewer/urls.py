from django.conf.urls import patterns, url

# Create your urls here.

import voxel_globe.voxel_viewer.views as views

urlpatterns = patterns('',
    url(r'^displayVoxelWorld/$', views.display_voxel_world, name='display_voxel_world'),
    url(r'^displayPotreeWorld/$', views.display_potree_world, name='display_potree_world'),
    url(r'^potreeDemo/$', views.display_potree_demo, name='display_potree_demo'),
    url(r'^potreeViewer/$', views.display_potree_viewer, name='display_potree_viewer'),
    url(r'^fetchPointCloud$', views.fetch_point_cloud,  name='fetch_point_cloud'),
    )
