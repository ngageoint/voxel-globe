from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.make_order_1, name='make_order_1'),
    url(r'^order/(?P<image_collection_id>\d+)$', views.make_order_2, name="make_order_2"),
    url(r'^order/(?P<image_collection_id>\d+)/(?P<scene_id>\d+)$', views.make_order_3, name="make_order_3"),
    url(r'^order/(?P<image_collection_id>\d+)/(?P<scene_id>\d+)/order$', views.make_order_4, name="make_order_4"),
    url(r'^status/(?P<task_id>[a-f\-\d]+)$', views.order_status, name='order_status')
)