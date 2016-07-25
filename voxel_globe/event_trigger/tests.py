from voxel_globe.meta import models
from voxel_globe.common_tests import VoxelGlobeTestCase
from django.core.urlresolvers import reverse

class EventTriggerTestCase(VoxelGlobeTestCase):
  def setUp(self):
    self.client = self.setupVoxelGlobeTestCase()

  def test_create_event_trigger(self):
    data = {
      'name' : 'shapely shape',
      'image_id': 305,
      'image_set_id' : 108,
      'points' : '1250.390625,-2507.2265625,2771.484375,-1076.3671875,4730.859375,-1579.1015625,3171.09375,-3551.3671875,1250.390625,-2507.2265625'
    }

    import json
    json_data = json.dumps(data)

    response = self.client.post('/apps/event_trigger/create_event_trigger',
      data=json_data, content_type="application/json; charset=utf-8")
    print response.status_code
    print response