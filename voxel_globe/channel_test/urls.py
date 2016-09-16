from django.conf.urls import url
import voxel_globe.channel_test.views as views

urlpatterns = [
    url(r'^$', views.channel_test, name='channel_test')
]