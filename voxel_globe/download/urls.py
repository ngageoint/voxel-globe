from django.conf.urls import patterns, url
import voxel_globe.download.views as views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^tiepoint$', views.tiepoint, name='tiepoint'),
    url(r'^control_point$', views.control_point, name='control_point'),
    url(r'^point_cloud$', views.point_cloud_ply, name='point_cloud_ply'),
    url(r'^cameras$', views.cameras_krt, name='cameras_krt'),
)