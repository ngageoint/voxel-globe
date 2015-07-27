from ..common_tasks import app, VipTask
from voxel_globe.serializers.numpyjson import NumpyAwareJSONEncoder
import voxel_globe.meta.models

import numpy
import json

@app.task(base=VipTask, bind=True)
def addTiePoint(self, *args, **kwargs):
  tp = voxel_globe.meta.models.TiePoint.create(*args, **kwargs);
  tp.service_id = self.request.id;
  tp.save();
  return tp.id;

@app.task(base=VipTask, bind=True)
def updateTiePoint(self, id, xc, y, *args, **kwargs):
  tp = voxel_globe.meta.models.TiePoint.objects.get(id=id);
  tp.service_id = self.request.id;
  #for key, val in kwargs.iteritems():
  #  tp.
  tp.point = 'POINT(%s %s)' % (xc,y);
  tp.update();
  return tp.id;

@app.task
def fetchCameraFrustum(**kwargs):
  from ..meta.tools import projectPoint
  from voxel_globe.tools.camera import get_kto
  try:
    imageId = int(kwargs["imageId"])
#    image = voxel_globe.meta.models.Image.objects.get(id=imageId)
    size = int(kwargs.pop('size', 100)); #Size in meters
    historyId = kwargs.pop('history', None)
    output = kwargs.pop('output', 'json')
    
    if historyId:
      historyId = int(historyId);
    history = voxel_globe.meta.models.History.to_dict(historyId)

    image = voxel_globe.meta.models.Image.objects.get(id=imageId).history(history)

    if image.camera:
      w = image.imageWidth;
      h = image.imageHeight;
      K, T, llh = get_kto(image, history);
      llh1 = projectPoint(K, T, llh, numpy.array([0]), numpy.array([0]), distances=0) 
      llh2 = projectPoint(K, T, llh, numpy.array([0,w,w,0]), numpy.array([0,0,h,h]), distances=size)
  
      llh2['lon'] = numpy.concatenate((llh1['lon'], llh2['lon']))
      llh2['lat'] = numpy.concatenate((llh1['lat'], llh2['lat']))
      llh2['h']   = numpy.concatenate((llh1['h'],   llh2['h']))
      
      if output == 'json':
        return json.dumps(llh2, cls=NumpyAwareJSONEncoder);
      elif output == 'kml':
        kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
  <name>KmlFile</name>
  <Style id="s_ylw-pushpin">
    <IconStyle>
      <scale>1.1</scale>
      <Icon>
        <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
      </Icon>
      <hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
    </IconStyle>
  </Style>
  <StyleMap id="m_ylw-pushpin">
    <Pair>
      <key>normal</key>
      <styleUrl>#s_ylw-pushpin</styleUrl>
    </Pair>
    <Pair>
      <key>highlight</key>
      <styleUrl>#s_ylw-pushpin_hl</styleUrl>
    </Pair>
  </StyleMap>
  <Style id="s_ylw-pushpin_hl">
    <IconStyle>
      <scale>1.3</scale>
      <Icon>
        <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
      </Icon>
      <hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
    </IconStyle>
  </Style>
  <Placemark>
    <name>Untitled Path</name>
    <styleUrl>#m_ylw-pushpin</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <altitudeMode>absolute</altitudeMode>
      <coordinates>'''
        for x in [0,1,0,2,0,3,0,4,3,2,1,4]:
          kml += '%0.12g,%0.12g,%0.12g ' % (llh2['lon'][x], llh2['lat'][x], llh2['h'][x]);
        kml += '''      </coordinates>
    </LineString>
  </Placemark>
</Document>
</kml>'''
        return kml;
  except voxel_globe.meta.models.Image.DoesNotExist:
    pass;
  
  return '';
  
  
@app.task
def fetchCameraRay(**kwargs):
  from ..meta.tools import projectPoint
  from voxel_globe.tools.camera import get_kto
  try:
    imageId = int(kwargs["imageId"])
#    image = voxel_globe.meta.models.Image.objects.get(id=imageId)
    height = int(kwargs.pop('height', 0))
    historyId = kwargs.pop('history', None)
    if historyId:
      historyId = int(historyId);
    history = voxel_globe.meta.models.History.to_dict(historyId)

    image = voxel_globe.meta.models.Image.objects.get(id=imageId).history(history)
    x = int(kwargs.pop('X', image.imageWidth/2))
    y = int(kwargs.pop('Y', image.imageHeight/2))
  
    if image.camera:
      K, T, llh = get_kto(image, history);
      llh1 = projectPoint(K, T, llh, numpy.array([x]), numpy.array([y]), distances=0) 
      llh2 = projectPoint(K, T, llh, numpy.array([x]), numpy.array([y]), zs=numpy.array([height]))

      llh2['lon'] = numpy.concatenate((llh1['lon'], llh2['lon']))
      llh2['lat'] = numpy.concatenate((llh1['lat'], llh2['lat']))
      llh2['h']   = numpy.concatenate((llh1['h'], llh2['h']))

      return json.dumps(llh2, cls=NumpyAwareJSONEncoder);
  except voxel_globe.meta.models.Image.DoesNotExist:
    pass

  return '';
