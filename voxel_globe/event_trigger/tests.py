from voxel_globe.meta import models
from voxel_globe.common_tests import VoxelGlobeTestCase
from django.core.urlresolvers import reverse

class EventTriggerTestCase(VoxelGlobeTestCase):
  def setUp(self):
    self.client = self.setupVoxelGlobeTestCase()

  def test_create_event_trigger(self):

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

    response = self.client.post('/meta/rest/auto/sattelsite/', data=json_data,
      content_type="application/json; charset=utf-8")
    sites = models.SattelSite.objects.all()
    self.assertEqual(len(sites), 1)
    site_id = sites[0].id

    response = self.client.post(reverse('create_site:make_order'), 
      {'sattel_site_id': site_id})

    self.assertTrue(len(models.Image.objects.all()) >= 5)
    self.assertTrue(len(models.ImageSet.objects.all()) >= 1)

    data = {
      'name' : 'shapely shape',
      'image_id': models.Image.objects.all()[0].id,
      'image_set_id' : models.ImageSet.objects.all()[0].id,
      'points' : '1250.390625,-2507.2265625,2771.484375,-1076.3671875,4730.859375,-1579.1015625,3171.09375,-3551.3671875,1250.390625,-2507.2265625',
      'site_id': models.SattelSite.objects.all()[0].id
    }

    json_data = json.dumps(data)

    response = self.client.post('/apps/event_trigger/create_event_trigger', 
      data=json_data, content_type="application/json; charset=utf-8")
    self.assertEqual(response.status_code, 200)
    
    with voxel_globe.tools.storage_dir('event_trigger_ply') as ply_dir:
      num_files = len([name for name in os.listdir(ply_dir)])
      filepath = os.path.join(ply_dir, 'mesh_%d.ply' % num_files)

  def tearDown(self):
    self.tearDownVoxelGlobeTestCase()