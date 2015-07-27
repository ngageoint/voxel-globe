from rest_framework import serializers
from rest_framework_gis import serializers as serializers_gis

class VipModelSerializer(serializers_gis.GeoModelSerializer):
  def save_object(self, obj, **kwargs):
    #Turn save into HISTORY save, AKA update.
    kwargs.pop('force_update', None);
    #This is something rest_framework adds for the update, but
    #Given the nature of how I update, this is not needed.
    kwargs.pop('force_insert', None);
    #This too is for advanced use, so I will ignore it for now

    if obj.pk is None: #if this is None
      #This is creating a new object
      obj.save(**kwargs)
    else:
      #else this is an update
      obj.update(**kwargs)

def serializerFactory(model):
  return type('AutoSerializer_%s' % model._meta.model_name, (VipModelSerializer,), 
              {'Meta': type('AutoMeta',  (object,), {'model':model})})


#import voxel_globe.meta.models
#class TiePointSerializer(serializers_gis.GeoModelSerializer):
#  class Meta:
#    model = voxel_globe.meta.models.TiePoint;
  
#Define custom serializers here