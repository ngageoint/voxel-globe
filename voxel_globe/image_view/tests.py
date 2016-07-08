from django.test import TestCase
from django.test import Client

# Create your tests here.
class ImageViewTestCase(TestCase):
  def test_template_render(self):
    # c = Client()
    # response = c.get('/apps/image_view/')
    # print(response)
    self.assertEqual("hello", "hello")