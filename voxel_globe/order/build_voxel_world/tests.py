from django.test import Client
from django.contrib.auth.models import User
from voxel_globe.meta import models
from voxel_globe.common_tests import VoxelGlobeTestCase
from celery import current_app
# import unittest.mock

class BuildVoxelWorldTestCase(VoxelGlobeTestCase):
  def setUp(self):
    # potentially, this should be pulled out further into voxel_globe.common_tests
    # mock.patch('celeryconfig.CELERY_ALWAYS_EAGER', True)  #nope
    current_app.conf.CELERY_ALWAYS_EAGER = True

    # create a new test client and log in
    self.user = User.objects.create_user('test', 'test@t.est', 'testy')
    self.user.save()
    self.client = Client()
    self.client.login(username='test', password='testy')

    # post request to create a new upload session, which we'll upload images to
    response = self.client.post('/apps/ingest/rest/uploadsession/', {  
      'name': 'apartments', 
      'metadata_type': 'krt',
      'payload_type': 'images'
    })

    import json
    response_json = json.loads(response.content)
    upload_session_id = response_json['id']

    response = self.client.get('/apps/ingest/addFiles?upload=' + str(upload_session_id))
    testFile = response.context['testFile']

    # find the directory with the images to be uploaded, and traverse it,
    # posting each image to ingest/uploadImage rest endpoint
    import os
    if not os.path.split(os.getcwd())[1] == 'test_images':
      os.chdir('./tests/test_images/')

    for dirpath, subdirs, files in os.walk(os.getcwd()):
      for f in files:
        with open(f) as fp:
          if f.endswith('.csv'):
            continue
          response = self.client.post('/apps/ingest/uploadImage', {
            'name': 'filedrop',
            'filename': f,
            'file': fp,
            'uploadSession': upload_session_id,
            'testFile': testFile
          })

    response = self.client.post('/apps/ingest/ingestFolderImage', {
      'uploadSession': upload_session_id
    })

    # there should be only 1 of each in the database at this point
    self.imageset = models.ImageSet.objects.all().order_by('name')[0]
    self.cameraset = models.CameraSet.objects.all().order_by('name')[0]
    self.scene = models.Scene.objects.all().order_by('name')[0]

  def test_voxel_world_template_render(self):
    response = self.client.get('/apps/order/voxel_world/')
    self.assertEqual(response.status_code, 200)

    templates = []
    for t in response.templates:
      templates.append(t.name)

    # test that the template renders correctly
    self.assertTrue('main/base.html' in templates)
    self.assertTrue('order/build_voxel_world/html/make_order.html' in templates)
    self.assertTrue('<h2>Build Voxel World</h2>' in response.content)

  def test_voxel_world_valid_form(self):
    base_form_data = {
      'image_set': self.imageset.id,
      'camera_set': self.cameraset.id,
      'scene': self.scene.id
    }

    bbox_min = self.scene.bbox_min
    bbox_max = self.scene.bbox_max
    default_voxel_size = self.scene.default_voxel_size

    meter_form_data = {
      'south_m': bbox_min[0],
      'west_m': bbox_min[1],
      'bottom_m': bbox_min[2],
      'north_m': bbox_max[0],
      'east_m': bbox_max[1],
      'top_m': bbox_max[2],
      'voxel_size_m': default_voxel_size[0]
    }

    import forms
    base_form = forms.OrderVoxelWorldBaseForm(data=base_form_data)
    meter_form = forms.OrderVoxelWorldMeterForm(data=meter_form_data)
    self.assertTrue(base_form.is_valid())
    self.assertTrue(meter_form.is_valid())

  def test_voxel_world_invalid_form(self):
    base_form_data = {
      'image_set': 3,
      'camera_set': 5
    }

    meter_form_data = {
      'south_m': 'hello',
      'west_m': 123,
      'bottom_m': 456
    }

    import forms
    base_form = forms.OrderVoxelWorldBaseForm(data=base_form_data)
    meter_form = forms.OrderVoxelWorldMeterForm(data=meter_form_data)
    self.assertFalse(base_form.is_valid())
    self.assertFalse(meter_form.is_valid())

    import json
    base_errors = json.dumps(base_form.errors)
    meter_errors = json.dumps(meter_form.errors)
    self.assertTrue('Select a valid choice. That choice is not one of the available choices.' in base_errors)
    self.assertTrue('This field is required.' in base_errors)
    self.assertTrue('Enter a number.' in meter_errors)
    self.assertTrue('This field is required.' in meter_errors)

  def test_build_voxel_world(self):
    bbox_min = self.scene.bbox_min
    bbox_max = self.scene.bbox_max
    default_voxel_size = self.scene.default_voxel_size

    data = {
      'south_m': bbox_min[0],
      'west_m': bbox_min[1],
      'bottom_m': bbox_min[2],
      'north_m': bbox_max[0],
      'east_m': bbox_max[1],
      'top_m': bbox_max[2],
      'voxel_size_m': default_voxel_size[0],
      'image_set': self.imageset.id,
      'camera_set': self.cameraset.id,
      'scene': self.scene.id
    }

    from django.core.urlresolvers import reverse
    response = self.client.post(reverse('order_build_voxel_world:make_order'), data)

    import re
    regex = re.compile(r'(\d+)$')
    task_id = regex.search(response['Location']).group()
    
    response = self.client.get('/apps/order/voxel_world/status/' + task_id)
    state_regex = re.compile(r'State: (\w+)<BR>')
    result_regex = re.compile(r'Result: (\w+)<BR>')
    reason_regex = re.compile(r'Reason: (\w+)<BR>')
    statelist = state_regex.split(response.content)
    if (len(statelist) > 1):
      state = statelist[1]
      print 'Build voxel world: ' + state
    resultlist = result_regex.split(response.content)
    if (len(resultlist) > 1):
      result = resultlist[1]
      print 'Build voxel world: ' + result
    reasonlist = reason_regex.split(response.content)
    if (len(reasonlist) > 1):
      reason = reasonlist[1]
      print 'Build voxel world: ' + reason
    
    # self.assertEqual(state, 'SUCCESS')

    # TODO next, check up on that voxel world in the actual database

  def tearDown(self):
    current_app.conf.CELERY_ALWAYS_EAGER = False
    # mock.patch('celeryconfig.CELERY_ALWAYS_EAGER', False)
    # TODO remove images from disk