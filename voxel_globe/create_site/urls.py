from django.conf.urls import patterns, url
import voxel_globe.create_site.views as views

urlpatterns = patterns('',
    url(r'^$', views.make_order, name='make_order')
    )