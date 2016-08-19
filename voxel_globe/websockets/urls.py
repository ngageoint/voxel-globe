from django.conf.urls import url, include
from rest_framework import routers
from voxel_globe.websockets import views

router = routers.DefaultRouter()
router.register(r'logmessage', views.LogMessageViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls))
]