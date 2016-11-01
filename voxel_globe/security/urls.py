from django.conf.urls import url
import voxel_globe.security.views as views

urlpatterns = [
    url(r'', views.images, name='images'),
]