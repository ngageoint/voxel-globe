from django.conf.urls import patterns, url

from voxel_globe.world import views

urlpatterns = patterns('',
    #url(r'^d/ok.html$', views.index, name='index')
    url(r'^$', views.index, name='world_index'),
    url(r'^search$', views.search, name='search'),
    url(r'^(?P<lat>-?\d+.?\d*)/result2/$', views.result2, name='result2'),
    url(r'^result/$', views.result, name='result'),
    url(r'^area$', views.area, name='area'),
)

