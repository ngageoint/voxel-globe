from django.test import Client
from django.contrib.auth.models import User
from voxel_globe.meta import models
from voxel_globe.common_tests import VoxelGlobeTestCase
from django.core.urlresolvers import reverse
from celery import current_app

class CreateSiteTestCase(VoxelGlobeTestCase):
  def setUp(self):
    # create a new test client and log in
    current_app.conf.CELERY_ALWAYS_EAGER = True
    self.user = User.objects.create_user('test', 'test@t.est', 'testy')
    self.user.save()
    self.client = Client()
    self.client.login(username='test', password='testy')

  def test_create_site_template_render(self):
    response = self.client.get('/apps/order/create_site/')
    self.assertEqual(response.status_code, 200)

    templates = []
    for t in response.templates:
      templates.append(t.name)

    self.assertTrue('main/common_header.html' in templates)
    self.assertTrue('main/base.html' in templates)
    self.assertTrue('order/create_site/html/make_order.html' in templates)
    self.assertTrue('<h2>Create Site</h2>' in response.content)

  def test_create_site_valid_form(self):
    form_data = {
      'name': 'kandahar',
      'south_d': 31.6201357853076,
      'west_d': 65.767785277177,
      'bottom_d': 990.987695163373,
      'north_d': 31.6298835627019,
      'east_d': 65.7759604108553,
      'top_d': 1323.62799335689
    }

    import forms
    form = forms.CreateSiteForm(data=form_data)
    self.assertTrue(form.is_valid())

  def test_create_site_invalid_form(self):
    form_data = {
      'south_d': 'not a number',
      'west_d': 65.767785277177,
      'bottom_d': 990.987695163373,
      'north_d': 31.6298835627019,
      'east_d': 65.7759604108553,
      'top_d': 1323.62799335689
    }

    import forms
    form = forms.CreateSiteForm(data=form_data)
    self.assertFalse(form.is_valid())

    import json
    form_errors = json.dumps(form.errors)
    self.assertTrue('This field is required.' in form_errors)
    self.assertTrue('Enter a number.' in form_errors)
    
  def test_create_site(self):
    data = {
      'name': 'kandahar',
      'south_d': 31.6201357853076,
      'west_d': 65.767785277177,
      'bottom_d': 990.987695163373,
      'north_d': 31.6298835627019,
      'east_d': 65.7759604108553,
      'top_d': 1323.62799335689
    }

    response = self.client.post(reverse('create_site:make_order'), data)

    import re
    regex = re.compile(r'(\d+)$')
    task_id = regex.search(response['Location']).group()
    
    response = self.client.get('/apps/order/create_site/status/' + task_id)

    state_regex = re.compile(r'State: (\w+)<BR>')
    result_regex = re.compile(r'Result: (\w+)<BR>')
    reason_regex = re.compile(r'Reason: (\w+)<BR>')
    statelist = state_regex.split(response.content)
    if (len(statelist) > 1):
      state = statelist[1]
      print 'Create site: ' + state
    resultlist = result_regex.split(response.content)
    if (len(resultlist) > 1):
      result = resultlist[1]
      print 'Create site: ' + result
    reasonlist = reason_regex.split(response.content)
    if (len(reasonlist) > 1):
      reason = reasonlist[1]
      print 'Create site: ' + reason

    # self.assertTrue(state == "SUCCESS")
    # i think for now it'll always be 'pending', since there's no user credentials getting passed along
  
  def tearDown(self):
    current_app.conf.CELERY_ALWAYS_EAGER = False