from django.conf.urls import patterns, url, include
from voxel_globe.ingest import views

urlpatterns = patterns('',
    url(r'^$', views.chooseSession, name='chooseSession'), #page 1
    url(r'^addFiles$', views.addFiles, name='addFiles'),   #page 2
    url(r'^ingestFolder$', views.ingestFolder, name="ingestFolder"),#page 3

    #Upload endpoint
    url(r'^upload$', views.upload, name="uploadEndpoint"),

    #REST end points
    url(r'^rest/', include(views.router.urls)),
)