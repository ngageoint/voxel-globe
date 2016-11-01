from django.conf.urls import url
import voxel_globe.create_site.views as views

urlpatterns = [
    url(r'^$', views.make_order, name='make_order')
]