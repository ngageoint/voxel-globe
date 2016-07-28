from voxel_globe.meta import models
from voxel_globe.common_tests import VoxelGlobeTestCase
import urllib2, ssl, os, zipfile, shutil

class BuildVoxelWorldTestCase(VoxelGlobeTestCase):
  def setUp(self):
    self.client = self.setupVoxelGlobeTestCase()

    # post request to create a new upload session, which we'll upload images to
    response = self.client.post('/apps/ingest/rest/uploadsession/', {  
      'name': 'capitol', 
      'metadata_type': 'krt',
      'payload_type': 'images'
    })

    import json
    response_json = json.loads(response.content)
    upload_session_id = response_json['id']

    response = self.client.get('/apps/ingest/addFiles?upload=' + str(upload_session_id))
    testFile = response.context['testFile']
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib2.urlopen('https://vsi-ri.com/data/pvd_2006_capitol_images_and_cameras.zip', context=ctx)

    self.dir_url = os.path.join(os.getenv('VIP_TEMP_DIR'), 'test_images')
    if not os.path.exists(self.dir_url):
      os.mkdir(self.dir_url)

    zip_url = os.path.join(self.dir_url, 'zipfile')
    
    with open(zip_url, 'w+') as z:
      z.write(response.read())

    zip_ref = zipfile.ZipFile(zip_url, 'r')
    zip_ref.extractall(self.dir_url)
    zip_ref.close()

    os.remove(zip_url)

    response = self.client.get('/apps/ingest/addFiles?upload=' + str(upload_session_id))
    testFile = response.context['testFile']

    image_count = 0;

    os.chdir(self.dir_url)

    for dirpath, subdirs, files in os.walk(self.dir_url):
      for f in files:
        with open(f) as fp:
          if f.endswith('.png'):
            image_count += 1
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

    filelist = [f for f in os.listdir(".")]
    for f in filelist:
      os.remove(f)

    # there should be only 1 of each in the database at this point
    self.imageset = models.ImageSet.objects.all()[0]
    self.cameraset = models.CameraSet.objects.all()[0]
    self.scene = models.Scene.objects.all()[0]

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

    bbox_min = [-0.3, -0.3, -0.1]
    bbox_max = [0.3, 0.3, 0.3]
    default_voxel_size = [0.006]

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
    bbox_min = [-0.3, -0.3, -0.1]
    bbox_max = [0.3, 0.3, 0.3]
    default_voxel_size = [0.3]

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
    self.assertEqual(len(models.VoxelWorld.objects.all()), 1)

  def tearDown(self):
    shutil.rmtree(self.dir_url)
    self.tearDownVoxelGlobeTestCase()