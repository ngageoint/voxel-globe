from django.conf.urls import patterns, url
import voxel_globe.order.create_site.views as views

urlpatterns = patterns('',
    url(r'^$', views.make_order, name='make_order'),
    url(r'^status/(?P<task_id>[a-f\-\d]+)$', views.order_status, name='order_status')
    )