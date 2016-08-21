from django.conf.urls import patterns, url
import voxel_globe.task.views

urlpatterns = patterns('',
    url(r'^status/$', voxel_globe.task.views.status, name='status'),
    url(r'^revoke/$', voxel_globe.task.views.revoke, name='revoke'),
    url(r'^mark_as_read/$', voxel_globe.task.views.mark_as_read, name='mark_as_read')
)