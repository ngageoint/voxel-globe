from django.conf.urls import patterns, url

# Create your urls here.

import voxel_globe.voxel_viewer.views as views

urlpatterns = patterns('',
    url(r'^fetchPointCloud$', views.fetch_point_cloud,  name='fetch_point_cloud'),
    url(r'^viewPointCloud$', views.view_point_cloud,  name='view_point_cloud'),
    url(r'^ingestPointCloud$', views.ingest_point_cloud,  name='ingest_point_cloud'),
    )
