from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
  url(r'^$', views.make_order, name='make_order'),
  url(r'^status/(?P<task_id>[a-f\-\d]+)$', views.order_status, name='order_status')
)