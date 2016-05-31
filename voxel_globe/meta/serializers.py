from rest_framework import serializers
from rest_framework_gis import serializers as serializers_gis

def serializerFactory(model):
  attributes = {'Meta': type('AutoMeta',  (object,), {'model':model})}
  attributes.update({ro_name:serializers.ReadOnlyField() for ro_name in getattr(model, 'readonly_fields', ())})
  return type('AutoSerializer_%s' % model._meta.model_name, 
              (serializers_gis.GeoModelSerializer,), attributes)
