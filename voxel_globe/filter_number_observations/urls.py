from django.conf.urls import patterns, url
import voxel_globe.filter_number_observations.views as views

urlpatterns = patterns('',
    url(r'^$', views.make_order, name='make_order'),
    url(r'^status/(?P<task_id>\d+)$', views.order_status, name="order_status"),
    )