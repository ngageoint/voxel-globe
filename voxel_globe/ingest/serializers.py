from rest_framework import serializers

import voxel_globe.ingest.models

class UploadSessionSerializer(serializers.ModelSerializer):
  #directory = serializers.RelatedField(many=True, read_only=True)
  class Meta(object):
    model = voxel_globe.ingest.models.UploadSession
    fields = ('file',)
    read_only_fields = ('file',)
#Add all the fields
fn = map(lambda x:x.name, voxel_globe.ingest.models.UploadSession._meta.fields)
#Except owner
fn.remove('owner')
#Add them to the existing list
UploadSessionSerializer.Meta.fields = UploadSessionSerializer.Meta.fields + \
                                      tuple(fn)
del fn #clean up

# class DirectorySerializer(serializers.ModelSerializer):
#   class Meta(object):
#     model = voxel_globe.ingest.models.Directory
#     fields = ('id', 'name', 'file', 'session')
#     read_only_fields = ('file',)

class FileSerializer(serializers.ModelSerializer):
  class Meta:
    model = voxel_globe.ingest.models.File
    fields = ('id', 'name', 'session', 'completed')

#Huge Security. Exposes Owner which exposes the password hash
#def NestFactory(serializer):
#  return type('Nested', (serializer,), 
#              {'Meta': type('Nested_Meta', (serializer.Meta,), {'depth':1})})