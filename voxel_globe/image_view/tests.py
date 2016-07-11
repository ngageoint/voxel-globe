from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

# Create your tests here.
class ImageViewTestCase(TestCase):
  def test_template_render(self):
    c = Client()

    # when not logged in, user should be unable to view this page
    # 302 = status code for login redirect
    response = c.get('/apps/image_view/')
    self.assertEqual(response.status_code, 302)

    # now create user, log in and make the valid request
    user = User.objects.create_user('test', 'test@t.est', 'testy')
    user.save()
    c.login(username='test', password='testy')
    response = c.get('/apps/image_view/')
    self.assertEqual(response.status_code, 200)

    templates = []
    for t in response.templates:
      templates.append(t.name)

    self.assertTrue('main/common_header.html' in templates)
    self.assertTrue('main/base.html' in templates)
    self.assertTrue('image_view/html/image_view.html' in templates)
    self.assertTrue('<h2>Image View</h2>' in response.content)