from rest_framework import serializers

import voxel_globe.ingest.models

class UploadSessionSerializer(serializers.ModelSerializer):
  #directory = serializers.RelatedField(many=True, read_only=True)
  class Meta(object):
    model = voxel_globe.ingest.models.UploadSession;
    fields = ('id', 'name', 'directory', 'sensorType')
    read_only_fields = ('directory',)

class DirectorySerializer(serializers.ModelSerializer):
  class Meta(object):
    model = voxel_globe.ingest.models.Directory;
    fields = ('id', 'name', 'file', 'session')
    read_only_fields = ('file',)

class FileSerializer(serializers.ModelSerializer):
  class Meta:
    model = voxel_globe.ingest.models.File;
    fields = ('id', 'name', 'directory', 'completed')

def NestFactory(serializer):
  return type('Nested', (serializer,), 
              {'Meta': type('Nested_Meta', (serializer.Meta,), {'depth':1})});