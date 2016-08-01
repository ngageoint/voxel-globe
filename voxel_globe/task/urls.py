from django.conf.urls import url
import voxel_globe.task.views

urlpatterns = [
    url(r'^status/(?P<task_id>[a-f\-\d]+)$', voxel_globe.task.views.status, name='status'),
    url(r'^list/$', voxel_globe.task.views.listQueues, name='list')
]