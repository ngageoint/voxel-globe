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
    url(r'^apps/event_trigger/', include('voxel_globe.event_trigger.urls', 
        namespace='event_trigger')),
    url(r'^apps/ingest/', include('voxel_globe.ingest.urls', 
        namespace='ingest')),
    url(r'^apps/ingest_controlpoint/', include('voxel_globe.ingest_controlpoint.urls', 
        namespace='ingest_controlpoint')),
    url(r'^apps/order/sfm/', include('voxel_globe.order.visualsfm.urls', 
        namespace='order_visualsfm')),
    url(r'^apps/order/voxel_world/', 
        include('voxel_globe.order.build_voxel_world.urls', 
        namespace='order_build_voxel_world')),
    url(r'^apps/order/error_point_cloud/', 
        include('voxel_globe.order.error_point_cloud.urls', 
        namespace='order_error_point_cloud')),
    url(r'^apps/order/threshold_point_cloud/', 
        include('voxel_globe.order.threshold_point_cloud.urls', 
        namespace='order_threshold_point_cloud')),
    url(r'^apps/order/tiepoint_registration/', 
        include('voxel_globe.order.tiepoint_registration.urls', 
        namespace='order_tiepoint_registration')),
    url(r'^apps/order/tiepoint_error_calculation/', 
        include('voxel_globe.order.tiepoint_error_calculation.urls', 
        namespace='order_tiepoint_error_calculation')),
    url(r'^apps/order/height_map/', 
        include('voxel_globe.order.height_map.urls', 
        namespace='order_height_map')),
    url(r'^apps/order/dem_error/', 
        include('voxel_globe.order.dem_error.urls', 
        namespace='dem_error')),
    url(r'^apps/order/filter_number_observations/', 
        include('voxel_globe.order.filter_number_observations.urls', 
        namespace='filter_number_observations')),
    url(r'^download/', 
        include('voxel_globe.download.urls', 
        namespace='download')),
    url(r'^apps/order/create_site/', 
        include('voxel_globe.order.create_site.urls', 
        namespace='create_site')),
    url(r'^apps/image_view/', 
        include('voxel_globe.image_view.urls', 
        namespace='image_view')),
    url(r'^apps/event_trigger/', 
        include('voxel_globe.event_trigger.urls', 
        namespace='event_trigger')),
)
