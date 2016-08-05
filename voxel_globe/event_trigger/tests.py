from voxel_globe.meta import models
from voxel_globe.common_tests import VoxelGlobeTestCase
from django.core.urlresolvers import reverse
from django import forms

class EventTriggerTestCase(VoxelGlobeTestCase):
  def setUp(self):
    self.client = self.setupVoxelGlobeTestCase()
    data = {
      'name' : 'Iran Docks',
      '_attributes': {'web': True},
      'bbox_min' : {
        'type': 'Point',
        'coordinates': [56.0620087320882448, 27.0975168703971754, -29.2682039794486251]
      },
      'bbox_max': {
        'type': 'Point',
        'coordinates': [56.0754837786924654, 27.1113411374972060, 436.6457609398668751]
      }
    }

    import json
    json_data = json.dumps(data)

    response = self.client.post('/meta/rest/auto/sattelsite/', data=json_data,
      content_type="application/json; charset=utf-8")
    sites = models.SattelSite.objects.all()
    self.assertEqual(len(sites), 1)
    site_id = sites[0].id

    response = self.client.post(reverse('create_site:make_order'), 
      {'sattel_site_id': site_id})

    self.assertTrue(len(models.Image.objects.all()) >= 8)
    self.assertEqual(len(models.ImageSet.objects.all()), 1)

  def test_create_run_event_trigger(self):
    site_id = models.SattelSite.objects.all()[0].id
    data = {
      'name' : 'shapely shape',
      'image_id': models.Image.objects.all()[0].id,
      'image_set_id' : models.ImageSet.objects.all()[0].id,
      'points' : '6181.0546875,1724.9267578125,6191.5283203125,1696.728515625,6356.689453125,1759.5703125,6344.6044921875,1786.1572265625,6181.0546875,1724.9267578125',
      'site_id': site_id
    }

    response = self.client.post('/apps/event_trigger/create_event_trigger', 
      data=data)
    self.assertEqual(response.status_code, 200)
    event_triggers = models.SattelEventTrigger.objects.all()
    self.assertEqual(len(event_triggers), 1)
    self.assertEqual(event_triggers[0].name, 'shapely shape')
    self.assertTrue(len(models.SattelGeometryObject.objects.all()) >= 2)

    response = self.client.post('/apps/event_trigger/run_event_trigger', 
      data={'site': site_id})
    self.assertEqual(response.status_code, 200)
    results = models.SattelEventResult.objects.all()
    self.assertTrue(len(results) >= 7)
    for result in results:
      if result.reference_image == result.mission_image:
        self.assertEqual(result.score, 0)
      else:
        self.assertTrue(result.score > 0)

  def tearDown(self):
    self.tearDownVoxelGlobeTestCase()

