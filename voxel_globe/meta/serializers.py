from rest_framework import serializers
from rest_framework_gis import serializers as serializers_gis

def serializerFactory(model):
  return type('AutoSerializer_%s' % model._meta.model_name, (serializers_gis.GeoModelSerializer,), 
              {'Meta': type('AutoMeta',  (object,), {'model':model})})
