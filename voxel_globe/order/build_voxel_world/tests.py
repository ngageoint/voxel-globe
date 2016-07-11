from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
import voxel_globe

class BuildVoxelWorldTestCase(APITestCase):
  # Test that the views file renders the correct template

  def setUp(self):
    # potentially, this should be pulled out further - a universal setup method?

    # create a new test client
    self.user = User.objects.create_user('test', 'test@t.est', 'testy')
    self.user.save()

    # log the client in to the Django Client and the APIClient
    self.client = Client()
    self.client.login(username='test', password='testy')

    # post request to create a new session, which we'll upload images to
    response = self.client.post('/apps/ingest/rest/uploadsession/', {  
      'name': 'apartments', 
      'metadata_type': 'krt',
      'payload_type': 'images'
    })

    import json
    response_json = json.loads(response.content)
    upload_session_id = response_json['id']
    
    response = self.client.get('/apps/ingest/addFiles?upload=' + str(upload_session_id))

    import os
    if not os.path.split(os.getcwd())[1] == 'test_images':
      os.chdir('./tests/test_images/')
    # filesList = []

    for dirpath, subdirs, files in os.walk(os.getcwd()):
      for f in files:
        with open(f) as fp:
          response = self.client.post('/apps/ingest/uploadImage', {'name': f, 'file': fp})
          print response.content

        # filesList.append(os.path.join(dirpath, f))

    # response = self.client.post('/apps/ingest/uploadImage', {
    #   'uploadSession': upload_session_id,
    #   'FILES': filesList
    # })

    print os.listdir('/tmp/ingest')

    print upload_session_id
    response = self.client.post('/apps/ingest/ingestFolderImage', {
      'uploadSession': upload_session_id
    })
    print response.content

    self.assertTrue('get task status' in response.content)

    task_number_index = response.content.find('Task') + 5
    task_number_dirty = response.content[task_number_index : task_number_index + 4]
    import re
    task_number = re.sub('[^0-9]','', task_number_dirty)
    
    response = self.client.get('/apps/task/status/' + str(task_number))
    import time

    for i in range(0, 5):
      print response.content
      time.sleep(5)

    print voxel_globe.meta.models.ImageSet.objects.all().order_by('name')

    self.scene = {
      'id': 1,
      'geolocated': True
    }


  def test_template_render(self):
    response = self.client.get('/apps/order/voxel_world/')
    self.assertEqual(response.status_code, 200)

    templates = []
    for t in response.templates:
      templates.append(t.name)

    self.assertTrue('main/common_header.html' in templates)
    self.assertTrue('main/base.html' in templates)
    self.assertTrue('order/build_voxel_world/html/make_order.html' in templates)
    self.assertTrue('<h2>Build Voxel World</h2>' in response.content)

  def test_voxel_world_form(self):
    # TODO
    response = self.client.get('/meta/rest/auto/scene/1')
    # self.scene = ???

    # data = response.json()

    # base_form_data = {
    #   'image_set': 1,
    #   'camera_set': 1,
    #   'scene': 1 todo
    # }

    # meter_form_data = {
    #   'south_m': data['bbox_min']['coordinates'][0],
    #   'west_m': data['bbox_min']['coordinates'][1],
    #   'bottom_m': data['bbox_min']['coordinates'][2],
    #   'north_m': data['bbox_max']['coordinates'][0],
    #   'east_m': data['bbox_max']['coordinates'][1],
    #   'top_m': data['bbox_max']['coordinates'][2],
    #   'voxel_size_m': data['default_voxel_size']['coordinates'][0]
    # }

    # base_form_data = {
    #   'image_set': 1,
    #   'camera_set': 1,
    #   'scene': 1
    # }

    meter_form_data = {
      'south_m': 41.8230012474629,
      'west_m': -71.4185233316793,
      'bottom_m': -30.7273,
      'north_m': 41.8338053050743,
      'east_m': -71.4047767017349,
      'top_m': 369.2727,
      'voxel_size_m': 0.6
    }

    import forms
    # base_form = forms.OrderVoxelWorldBaseForm(data=base_form_data)
    meter_form = forms.OrderVoxelWorldMeterForm(data=meter_form_data)
    # print base_form.errors
    # self.assertTrue(base_form.is_valid())
    self.assertTrue(meter_form.is_valid())

  def test_build_voxel_world(self):
    # TODO based on the scene, get the image and camera set ids
    image_set_id = 1
    camera_set_id = 1

    # TODO get from self.scene
    bbox = {'x_min': 41.8230012474629,
            'y_min': -71.4185233316793,
            'z_min': -30.7273,
            'x_max': 41.8338053050743,
            'y_max': -71.4047767017349,
            'z_max':  369.2727,
            'voxel_size': 0.6,
            'geolocated': self.scene['geolocated']}

    from voxel_globe.build_voxel_world import tasks
    task = tasks.run_build_voxel_model.apply_async(args=(image_set_id, 
          camera_set_id, self.scene['id'], bbox, 1, True))

    while not (task.state == 'SUCCESS' or task.state == 'FAILURE'):
      pass

    # print 'Build voxel world: %s, %s' % (task.state, task.result)

    # self.assertEqual(task.state, 'SUCCESS')

    # TODO next, check up on that voxel world in the actual database

  # def tearDown(self):
  #   os.chdir('../..')