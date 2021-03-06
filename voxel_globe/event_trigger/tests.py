from voxel_globe.meta import models
from voxel_globe.common_tests import VoxelGlobeTestCase
from django.core.urlresolvers import reverse
from django import forms

class EventTriggerTestCase(VoxelGlobeTestCase):
  def setUp(self):
    self.client = self.setupVoxelGlobeTestCase()
  def test_update_geometry_polygon(self):
    import json
    import voxel_globe.meta.models as models
    import brl_init
    import vpgl_adaptor_boxm2_batch as vpgl_adaptor

    image_set = models.ImageSet(name="foo")
    image_set.save()

    camera_set = models.CameraSet(name="bar", images=image_set)
    camera_set.save()

    image = models.Image(name="foo", image_width=1, image_height=1, 
                         number_bands=1, pixel_format='f', file_format='zoom')
    image.filename_path="bar"
    
    image.attributes = {'planet_rest_response': {'geometry': {'coordinates': \
      [[[56.119114650682164, 27.200333624676592], 
        [56.24739277512627, 27.302268549650677], 
        [56.322945431205206, 27.226150871777726], 
        [56.19470727840827, 27.12434691842213], 
        [56.119114650682164, 27.200333624676592]]]}}}

    image.save()
    image_set.images.add(image)

    with open('/tmp/myrpc.txt', 'w') as fid:
      fid.write('''LINE_OFF: 2199.95786962973
SAMP_OFF: 3299.93681480566
LAT_OFF: 27.0107983932873
LONG_OFF: 56.0363902428004
HEIGHT_OFF: 245.550203994236
LINE_SCALE: 2197.64180214547
SAMP_SCALE: 3296.97019610174
LAT_SCALE: -0.107960105751161
LONG_SCALE: 0.126520164110941
HEIGHT_SCALE: 141.752709944384
LINE_NUM_COEFF_1: -0.0024565013772073
LINE_NUM_COEFF_2: 1.17377445766184
LINE_NUM_COEFF_3: 1.30095901146345
LINE_NUM_COEFF_4: -0.000188491953355339
LINE_NUM_COEFF_5: 0.00306946589178833
LINE_NUM_COEFF_6: 0.000585326974115261
LINE_NUM_COEFF_7: 0.000657300733886658
LINE_NUM_COEFF_8: 0.000234127798636895
LINE_NUM_COEFF_9: 0.00097936767856325
LINE_NUM_COEFF_10: 3.90831477730178e-07
LINE_NUM_COEFF_11: 0.000161179161230342
LINE_NUM_COEFF_12: 0.00723337943463883
LINE_NUM_COEFF_13: 0.00707966855335754
LINE_NUM_COEFF_14: 2.20919180843239e-05
LINE_NUM_COEFF_15: 0.00856982214955269
LINE_NUM_COEFF_16: 0.00716916888806396
LINE_NUM_COEFF_17: 2.45499825728313e-05
LINE_NUM_COEFF_18: 0.00011637486515919
LINE_NUM_COEFF_19: 3.34638938403648e-05
LINE_NUM_COEFF_20: 1.00324656378471e-07
LINE_DEN_COEFF_1: 1
LINE_DEN_COEFF_2: 0.000148575566121153
LINE_DEN_COEFF_3: 3.33109206259576e-05
LINE_DEN_COEFF_4: 0.00012203839106374
LINE_DEN_COEFF_5: 0.000469401100377465
LINE_DEN_COEFF_6: 9.69389049981109e-05
LINE_DEN_COEFF_7: 2.70742305225499e-05
LINE_DEN_COEFF_8: -8.54202634402009e-05
LINE_DEN_COEFF_9: -0.000161592109514956
LINE_DEN_COEFF_10: 1.73174826003368e-05
LINE_DEN_COEFF_11: -5.73349540333628e-07
LINE_DEN_COEFF_12: -1.53068722126089e-05
LINE_DEN_COEFF_13: -1.17084193159117e-05
LINE_DEN_COEFF_14: -8.51510372553032e-07
LINE_DEN_COEFF_15: -1.80466089956319e-05
LINE_DEN_COEFF_16: -1.48674409169359e-05
LINE_DEN_COEFF_17: 1.72544581067044e-07
LINE_DEN_COEFF_18: -7.59977630338624e-06
LINE_DEN_COEFF_19: -6.82723988123299e-06
LINE_DEN_COEFF_20: -3.08469454777552e-07
SAMP_NUM_COEFF_1: -0.0017478785512101
SAMP_NUM_COEFF_2: 0.910394923019121
SAMP_NUM_COEFF_3: -0.745786249344129
SAMP_NUM_COEFF_4: -5.53172852705572e-05
SAMP_NUM_COEFF_5: 0.000948353228935995
SAMP_NUM_COEFF_6: 0.000298864514828254
SAMP_NUM_COEFF_7: -0.000242007607291905
SAMP_NUM_COEFF_8: 0.00111342376685003
SAMP_NUM_COEFF_9: -0.000535383165110758
SAMP_NUM_COEFF_10: -8.84481670079125e-07
SAMP_NUM_COEFF_11: 0.000118217548178094
SAMP_NUM_COEFF_12: 0.00523025251486188
SAMP_NUM_COEFF_13: 0.0054726104346157
SAMP_NUM_COEFF_14: -3.53871748240463e-05
SAMP_NUM_COEFF_15: -0.0048496312013046
SAMP_NUM_COEFF_16: -0.00410469518299708
SAMP_NUM_COEFF_17: 2.85618467641931e-05
SAMP_NUM_COEFF_18: -9.58265322689581e-05
SAMP_NUM_COEFF_19: -3.27933320422228e-05
SAMP_NUM_COEFF_20: -8.66313071123194e-08
SAMP_DEN_COEFF_1: 1
SAMP_DEN_COEFF_2: 0.000146286327744963
SAMP_DEN_COEFF_3: -5.40352119859342e-06
SAMP_DEN_COEFF_4: -4.81515209484682e-05
SAMP_DEN_COEFF_5: -0.000613975549603293
SAMP_DEN_COEFF_6: -0.000103378207963619
SAMP_DEN_COEFF_7: 4.8028390243135e-05
SAMP_DEN_COEFF_8: -0.000499094672255183
SAMP_DEN_COEFF_9: -0.000168192999237417
SAMP_DEN_COEFF_10: -3.62088997153893e-05
SAMP_DEN_COEFF_11: 8.96740073313948e-07
SAMP_DEN_COEFF_12: -1.58411883959929e-05
SAMP_DEN_COEFF_13: -1.6864724045683e-05
SAMP_DEN_COEFF_14: 4.9525089386063e-08
SAMP_DEN_COEFF_15: -2.26352376743834e-05
SAMP_DEN_COEFF_16: -1.7593030322958e-05
SAMP_DEN_COEFF_17: 1.25501903075052e-06
SAMP_DEN_COEFF_18: -6.73113280552874e-06
SAMP_DEN_COEFF_19: -6.63507788713566e-06
SAMP_DEN_COEFF_20: 4.3824336969942e-07''');


    camera = models.RpcCamera(name='foo', rpc_path='/tmp/myrpc.txt', 
                              image=image)
    camera.save()
    camera_set.cameras.add(camera)

    site = models.SattelSite(
        bbox_min='POINT(65.767785277177 31.6201357853076 990.987695163373)',
        bbox_max='POINT(65.7759604108553 31.6298835627019 1323.62799335689)',
        image_set=image_set, camera_set=camera_set)
    site.save()

    data = {
      'name': 'foo',
      'attributes': {'web': True},
      'origin': 'POINT(55.9128631156102216 26.9966789278463750 0)',
      'reference_image': image.id,
      'site': site.id,
      'event_areas': [],
      'reference_areas':[],
    }

    response = self.client.post('/meta/rest/auto/satteleventtrigger/', data=json.dumps(data),
      content_type="application/json; charset=utf-8")
    self.assertEqual(response.status_code, 201)
    sattel_trigger_id = response.data['id']

    data = {
      'name': 'bar',
      'attributes': {'web': True},
      'origin': 'POINT(11 22 33)',
      'site': site.id,
      'polygon': 'POLYGON((0 0 0, 0 0 0, 0 0 0, 0 0 0))'
    }

    response = self.client.post('/meta/rest/auto/sattelgeometryobject/', data=json.dumps(data),
      content_type="application/json; charset=utf-8")
    self.assertEqual(response.status_code, 201)
    sattelgeometryobject_id = response.data['id']

    data = {
      'image_id':image.id,
      'site_id':site.id,
      'points':'POLYGON((11.1 22, 33 44, 55 66, 11.1 22))',
      'sattelgeometryobject_id':sattelgeometryobject_id,
      'projection_mode': 'z-plane',
      'height':11.2
    }

    response = self.client.post(reverse('event_trigger:update_geometry_polygon'),
      data=data)
    self.assertEqual(response.status_code, 200)

    sattelgeometryobject = models.SattelGeometryObject.objects.get(id=sattelgeometryobject_id)
    print repr(sattelgeometryobject)

    data = {
      'image_id':image.id,
      'site_id':site.id,
      'sattelgeometryobject_id':sattelgeometryobject_id
    }

    response = self.client.get(reverse('event_trigger:get_event_geometry'),
      data=data)

    print response
    

    # vxl_camera = vpgl_adaptor.load_rational_camera_from_txt(camera.rpc_path)
    # point = vpgl_adaptor.project_point(vxl_camera, 55.9128631156102216, 26.9966789278463750, 9.987695163373)
    # print point

  def tearDown(self):
    self.tearDownVoxelGlobeTestCase()

