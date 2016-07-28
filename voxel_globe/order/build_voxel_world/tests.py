from voxel_globe.meta import models
from voxel_globe.common_tests import VoxelGlobeTestCase

# class BuildVoxelWorldTestCase(VoxelGlobeTestCase):
#   def setUp(self):
#     self.client = self.setupVoxelGlobeTestCase()

#     # post request to create a new upload session, which we'll upload images to
#     response = self.client.post('/apps/ingest/rest/uploadsession/', {  
#       'name': 'apartments', 
#       'metadata_type': 'krt',
#       'payload_type': 'images'
#     })

#     import json
#     response_json = json.loads(response.content)
#     upload_session_id = response_json['id']

#     response = self.client.get('/apps/ingest/addFiles?upload=' + str(upload_session_id))
#     testFile = response.context['testFile']

#     # find the directory with the images to be uploaded, and traverse it,
#     # posting each image to ingest/uploadImage rest endpoint
#     import os
#     if not os.path.split(os.getcwd())[1] == 'test_images':
#       os.chdir('./tests/test_images/')

#     for dirpath, subdirs, files in os.walk(os.getcwd()):
#       for f in files:
#         with open(f) as fp:
#           if f.endswith('.csv'):
#             continue
#           response = self.client.post('/apps/ingest/uploadImage', {
#             'name': 'filedrop',
#             'filename': f,
#             'file': fp,
#             'uploadSession': upload_session_id,
#             'testFile': testFile
#           })

#     response = self.client.post('/apps/ingest/ingestFolderImage', {
#       'uploadSession': upload_session_id
#     })

#     # there should be only 1 of each in the database at this point
#     self.imageset = models.ImageSet.objects.all().order_by('name')[0]
#     self.cameraset = models.CameraSet.objects.all().order_by('name')[0]
#     self.scene = models.Scene.objects.all().order_by('name')[0]

#   def test_voxel_world_template_render(self):
#     response = self.client.get('/apps/order/voxel_world/')
#     self.assertEqual(response.status_code, 200)

#     templates = []
#     for t in response.templates:
#       templates.append(t.name)

#     # test that the template renders correctly
#     self.assertTrue('main/base.html' in templates)
#     self.assertTrue('order/build_voxel_world/html/make_order.html' in templates)
#     self.assertTrue('<h2>Build Voxel World</h2>' in response.content)

#   def test_voxel_world_valid_form(self):
#     base_form_data = {
#       'image_set': self.imageset.id,
#       'camera_set': self.cameraset.id,
#       'scene': self.scene.id
#     }

#     bbox_min = self.scene.bbox_min
#     bbox_max = self.scene.bbox_max
#     default_voxel_size = self.scene.default_voxel_size

#     meter_form_data = {
#       'south_m': bbox_min[0],
#       'west_m': bbox_min[1],
#       'bottom_m': bbox_min[2],
#       'north_m': bbox_max[0],
#       'east_m': bbox_max[1],
#       'top_m': bbox_max[2],
#       'voxel_size_m': default_voxel_size[0]
#     }

#     import forms
#     base_form = forms.OrderVoxelWorldBaseForm(data=base_form_data)
#     meter_form = forms.OrderVoxelWorldMeterForm(data=meter_form_data)
#     self.assertTrue(base_form.is_valid())
#     self.assertTrue(meter_form.is_valid())

#   def test_voxel_world_invalid_form(self):
#     base_form_data = {
#       'image_set': 3,
#       'camera_set': 5
#     }

#     meter_form_data = {
#       'south_m': 'hello',
#       'west_m': 123,
#       'bottom_m': 456
#     }

#     import forms
#     base_form = forms.OrderVoxelWorldBaseForm(data=base_form_data)
#     meter_form = forms.OrderVoxelWorldMeterForm(data=meter_form_data)
#     self.assertFalse(base_form.is_valid())
#     self.assertFalse(meter_form.is_valid())

#     import json
#     base_errors = json.dumps(base_form.errors)
#     meter_errors = json.dumps(meter_form.errors)
#     self.assertTrue('Select a valid choice. That choice is not one of the available choices.' in base_errors)
#     self.assertTrue('This field is required.' in base_errors)
#     self.assertTrue('Enter a number.' in meter_errors)
#     self.assertTrue('This field is required.' in meter_errors)

#   def test_build_voxel_world(self):
#     bbox_min = self.scene.bbox_min
#     bbox_max = self.scene.bbox_max
#     default_voxel_size = self.scene.default_voxel_size

#     data = {
#       'south_m': bbox_min[0],
#       'west_m': bbox_min[1],
#       'bottom_m': bbox_min[2],
#       'north_m': bbox_max[0],
#       'east_m': bbox_max[1],
#       'top_m': bbox_max[2],
#       'voxel_size_m': default_voxel_size[0],
#       'image_set': self.imageset.id,
#       'camera_set': self.cameraset.id,
#       'scene': self.scene.id
#     }

#     # TODO
#     # For now, this segfaults. That's also what happens using the UI, so it's
#     # not a fault of the test suite. Once build_voxel_world is up and running,
#     # uncomment these:
    
#     # from django.core.urlresolvers import reverse
#     # response = self.client.post(reverse('order_build_voxel_world:make_order'), data)
#     # self.assertEqual(len(models.VoxelWorld.objects.all()), 1)

#   def tearDown(self):
#     self.tearDownVoxelGlobeTestCase()