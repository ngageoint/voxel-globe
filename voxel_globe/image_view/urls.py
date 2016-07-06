from django.conf.urls import patterns, url
import voxel_globe.image_view.views as views

urlpatterns = patterns('',
    url(r'^$', views.image_view, name='image_view')
    )