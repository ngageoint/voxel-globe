from django.conf.urls import patterns, include, url

from django.contrib import admin

#handler400 = 'world.views.error400page'
#AEN: THIS doesn't work!

import voxel_globe.main.views

urlpatterns = patterns('',
    #Admin site apps
    url(r'^admin/', include(admin.site.urls)),
    #Test app for development reasons
    url(r'^world/', include('voxel_globe.world.urls', namespace='world')),
    
    # pages
    #Main home page    
    url(r'', include('voxel_globe.main.urls', namespace='main')),
    
    #Placeholders
#    url(r'^apps/imageIngest/$', voxel_globe.main.views.imageIngest, name='imageIngest'),
    url(r'^apps/voxelCreator/$', voxel_globe.main.views.voxelCreator, name='voxelCreator'),
    url(r'^apps/voxelWorldViewer/$', voxel_globe.main.views.voxelWorldViewer, name='voxelWorldViewer'),
#    url(r'^apps/ingest/upload$', 'voxel_globe.ingest.views.upload', name="uploadEndpoint"),
#    url(r'^apps/ingest/$', 'voxel_globe.ingest.views.blah'),

    #REST auth endpoint
    url(r'^rest/', include('rest_framework.urls', namespace='rest_framework')),

    #apps
    url(r'^meta/', include('voxel_globe.meta.urls', namespace='meta')),
    url(r'^apps/task/', include('voxel_globe.task.urls', namespace='task')),
    url(r'^apps/tiepoint/', include('voxel_globe.tiepoint.urls', namespace='tiepoint')),
    url(r'^apps/voxel_viewer/', include('voxel_globe.voxel_viewer.urls', namespace='voxel_viewer')),
    url(r'^apps/ingest/', include('voxel_globe.ingest.urls', namespace='ingest')),
    url(r'^apps/order/sfm/', include('voxel_globe.order.visualsfm.urls', namespace='order_visualsfm')),
    url(r'^apps/order/voxel_world/', include('voxel_globe.order.build_voxel_world.urls', namespace='order_build_voxel_world')),
)
