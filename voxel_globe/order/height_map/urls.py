from django.conf.urls import patterns, url

# Create your urls here.

import voxel_globe.order.height_map.views as views

urlpatterns = patterns('',
    url(r'^$', views.make_order, name='make_order'),
    )
