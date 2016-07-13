from voxel_globe.common_tests import VoxelGlobeTestCase
from django.test import Client
from django.contrib.auth.models import User

# Create your tests here.
class ImageViewTestCase(VoxelGlobeTestCase):
  def setUp(self):
    # create a new test client and log in
    self.user = User.objects.create_user('test', 'test@t.est', 'testy')
    self.user.save()
    self.client = Client()
    self.client.login(username='test', password='testy')

  def test_image_view_template_render(self):
    response = self.client.get('/apps/image_view/')
    self.assertEqual(response.status_code, 200)

    templates = []
    for t in response.templates:
      templates.append(t.name)

    self.assertTrue('main/common_header.html' in templates)
    self.assertTrue('main/base.html' in templates)
    self.assertTrue('image_view/html/image_view.html' in templates)
    self.assertTrue('<h2>Image View</h2>' in response.content)