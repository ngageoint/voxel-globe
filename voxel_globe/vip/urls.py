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
#    url(r'^apps/imageIngest/$', voxel_globe.main.views.imageIngest, 
#        name='imageIngest'),
    url(r'^apps/voxelCreator/$', voxel_globe.main.views.voxelCreator, 
        name='voxelCreator'),
    url(r'^apps/voxelWorldViewer/$', voxel_globe.main.views.voxelWorldViewer, 
        name='voxelWorldViewer'),
#    url(r'^apps/ingest/upload$', 'voxel_globe.ingest.views.upload', 
#        name="uploadEndpoint"),

    #REST auth endpoint
    url(r'^rest/', include('rest_framework.urls', namespace='rest_framework')),

    #apps
    url(r'^meta/', include('voxel_globe.meta.urls', namespace='meta')),
    url(r'^apps/task/', include('voxel_globe.task.urls', namespace='task')),
    url(r'^apps/tiepoint/', include('voxel_globe.tiepoint.urls', 
        namespace='tiepoint')),
    url(r'^apps/voxel_viewer/', include('voxel_globe.voxel_viewer.urls', 
        namespace='voxel_viewer')),
    url(r'^apps/ingest/', include('voxel_globe.ingest.urls', 
        namespace='ingest')),
    url(r'^apps/sfm/', include('voxel_globe.visualsfm.urls', 
        namespace='visualsfm')),
    url(r'^apps/voxel_world/', 
        include('voxel_globe.build_voxel_world.urls', 
        namespace='build_voxel_world')),
    url(r'^apps/order/error_point_cloud/', 
        include('voxel_globe.order.error_point_cloud.urls', 
        namespace='order_error_point_cloud')),
    url(r'^apps/order/threshold_point_cloud/', 
        include('voxel_globe.order.threshold_point_cloud.urls', 
        namespace='order_threshold_point_cloud')),
    url(r'^apps/tiepoint_registration/', 
        include('voxel_globe.tiepoint_registration.urls', 
        namespace='order_tiepoint_registration')),
    url(r'^apps/height_map/', 
        include('voxel_globe.height_map.urls', 
        namespace='height_map')),
    url(r'^apps/filter_number_observations/', 
        include('voxel_globe.filter_number_observations.urls', 
        namespace='filter_number_observations')),
    url(r'^download/', 
        include('voxel_globe.download.urls', 
        namespace='download')),
    url(r'^apps/create_site/', 
        include('voxel_globe.create_site.urls', 
        namespace='create_site')),
    url(r'^apps/image_view/', 
        include('voxel_globe.image_view.urls', 
        namespace='image_view')),
    url(r'^apps/event_trigger/', 
        include('voxel_globe.event_trigger.urls', 
        namespace='event_trigger')),
    url(r'^apps/channels/', 
        include('voxel_globe.channel_test.urls', 
        namespace='channel_test')),
    url(r'^apps/websockets/', 
        include('voxel_globe.websockets.urls', 
        namespace='websockets')),

    #Other static protected assets
    url(r'^images/',
        include('voxel_globe.security.urls',
        namespace='security')) ,
)
