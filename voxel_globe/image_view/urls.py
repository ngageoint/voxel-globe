from django.conf.urls import url
import voxel_globe.image_view.views as views

urlpatterns = [
    url(r'^$', views.image_view, name='image_view')
]