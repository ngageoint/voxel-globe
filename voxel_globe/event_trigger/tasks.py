import os
from os import environ as env

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

from voxel_globe.common_tasks import shared_task, VipTask

@shared_task(base=VipTask, bind=True)
def event_trigger(self, sattel_site_id):
  import voxel_globe.meta.models as models
  import betr_adaptor as betr
  import vil_adaptor_betr_batch as vil
  import vpgl_adaptor_betr_batch as vpgl
  
  site = models.SattelSite.objects.get(id=sattel_site_id)
  self.update_state(state="PROCESSING", meta={"site_name": site.name})
  for event_trigger_index, etr in enumerate(site.satteleventtrigger_set.all()):
    for event_geometry_index, evt_obj in enumerate(etr.event_areas.all()):

      if not etr.reference_areas.all():
        continue

      ref_obj = etr.reference_areas.all()[0] #REDO

      ref_image = etr.reference_image
      ref_cam = ref_image.camera_set.get(cameraset=site.camera_set).select_subclasses()[0] #REDO

      (ref_image_vil_msi, ni, nj) = vil.load_image_resource(ref_image.filename_path)
      ref_image_vil = vil.multi_plane_view_to_grey(ref_image_vil_msi)

      #(ref_image_vil, ni, nj) = vil.load_image_resource(ref_image.filename_path)
      ref_cam_vpgl = vpgl.load_rational_camera_from_txt(ref_cam.rpc_path)
      # print 'load rcam',status

      betr_etr = betr.create_betr_event_trigger(etr.origin.x,etr.origin.y,etr.origin.z, 'rajaei_pier')
      print betr_etr.type

      rx = ref_obj.origin.x
      ry = ref_obj.origin.y
      rz = ref_obj.origin.z
      status = betr.add_event_trigger_object(betr_etr, 'pier_ref',rx,ry,rz,ref_obj.geometry_path,True)
      print 'add ref obj',status

      ex = evt_obj.origin.x
      ey = evt_obj.origin.y
      ez = evt_obj.origin.z
      status = betr.add_event_trigger_object(betr_etr, 'pier_evt',ex,ey,ez,evt_obj.geometry_path,False)
      print 'add evt obj',status

      for evt_image0 in site.image_set.images.all():
        (evt_image_vil_msi, ni, nj) =vil.load_image_resource(evt_image0.filename_path)
        evt_image_vil = vil.multi_plane_view_to_grey(evt_image_vil_msi)

        evt_cam = evt_image0.camera_set.get(cameraset=site.camera_set).select_subclasses()[0] #REDO
        evt_cam_vpgl = vpgl.load_rational_camera_from_txt(evt_cam.rpc_path)
        # print 'load rcam',status

        status = betr.set_event_trigger_data(betr_etr,ref_image_vil,ref_cam_vpgl, evt_image_vil, evt_cam_vpgl)
        print 'set data status', status

        (status, score) = betr.execute_event_trigger(betr_etr,'edgel_change_detection')
        print 'execute status', status, 'score(change)', score

        if status:
          models.SattelEventResult(name="Event %s, %s, %s" % (site.name, evt_image0.name, evt_obj.name),
                                   geometry=evt_obj, score=score, 
                                   reference_image=ref_image,
                                   mission_image=evt_image0).save()

  return {"site_name": site.name}
