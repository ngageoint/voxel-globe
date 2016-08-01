from django.conf.urls import url

# Create your urls here.

import voxel_globe.order.tiepoint_registration.views as views

urlpatterns = [
    url(r'^$', views.make_order_1, name='make_order_1'),
    url(r'^order/(?P<image_set_id>\d+)$', views.make_order_2, name="make_order_2"),
]
