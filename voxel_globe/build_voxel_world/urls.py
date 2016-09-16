from django.conf.urls import url
import views

urlpatterns = [
  url(r'^$', views.make_order, name='make_order'),
  url(r'^status/(?P<task_id>[a-f\-\d]+)$', views.order_status, name='order_status')
]