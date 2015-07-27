from django.conf.urls import patterns, url, include
from voxel_globe.ingest import views

urlpatterns = patterns('',
    url(r'^$', views.chooseSession, name='chooseSession'),
    url(r'^addFiles$', views.addFiles, name='addFiles'),
    url(r'^upload$', views.upload, name="uploadEndpoint"),
    url(r'^ingestFolder$', views.ingestFolder, name="ingestFolder"),

    url(r'^blah$', views.blah, name="blah_del_me"),

#   RESTful end points
    url(r'^rest/', include(views.router.urls)),
)