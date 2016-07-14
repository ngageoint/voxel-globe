from voxel_globe.meta import models
from voxel_globe.common_tests import VoxelGlobeTestCase
from django.core.urlresolvers import reverse

class CreateSiteTestCase(VoxelGlobeTestCase):
  def setUp(self):
    self.client = self.setupVoxelGlobeTestCase()

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
      'name' : 'kandahar',
      '_attributes': {'web': True},
      'bbox_min' : {
        'type': 'Point',
        'coordinates': [65.767785277177, 31.6201357853076, 990.987695163373]
      },
      'bbox_max': {
        'type': 'Point',
        'coordinates': [65.7759604108553, 31.6298835627019, 1323.62799335689]
      }
    }

    import json
    json_data = json.dumps(data)

    # TODO
    # Uncomment these to run the full test suite. These take a long time so
    # are commented out for ease in developing more tests.

    # response = self.client.post('/meta/rest/auto/sattelsite/', data=json_data,
    #   content_type="application/json; charset=utf-8")
    # sites = models.SattelSite.objects.all()
    # self.assertEqual(len(sites), 1)
    # site_id = sites[0].id

    # response = self.client.post(reverse('create_site:make_order'), 
    #   {'sattel_site_id': site_id})

    # self.assertTrue(len(models.Image.objects.all()) >= 5)
    # self.assertTrue(len(models.ImageSet.objects.all()) >= 1)

  def tearDown(self):
    self.tearDownVoxelGlobeTestCase()