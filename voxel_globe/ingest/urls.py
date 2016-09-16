from django.conf.urls import url, include
from voxel_globe.ingest import views

urlpatterns = [
    url(r'^$', views.chooseSession, name='chooseSession'), #page 1
    url(r'^addFiles$', views.addFiles, name='addFiles'),   #page 2
    url(r'^ingestFolderImage$', views.ingestFolderImage, name="ingestFolderImage"),#page 3
    url(r'^ingestFolderControlpoint$', views.ingestFolderControlpoint, name="ingestFolderControlpoint"),#page 3

    #Upload endpoint
    url(r'^uploadImage$', views.uploadImage, name="uploadImageEndpoint"),
    url(r'^uploadControlpoint$', views.uploadControlpoint, name="uploadControlpointEndpoint"),

    #REST end points
    url(r'^rest/', include(views.router.urls)),
]