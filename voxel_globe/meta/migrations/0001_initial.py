# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import voxel_globe.meta.models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('objectId', models.CharField(max_length=36, verbose_name=b'Object ID')),
                ('deleted', models.BooleanField(default=False, verbose_name=b'Object deleted')),
                ('focalLengthU', models.FloatField()),
                ('focalLengthV', models.FloatField()),
                ('principalPointU', models.FloatField()),
                ('principalPointV', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ControlPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('objectId', models.CharField(max_length=36, verbose_name=b'Object ID')),
                ('deleted', models.BooleanField(default=False, verbose_name=b'Object deleted')),
                ('description', models.TextField()),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('apparentPoint', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3, null=True, blank=True)),
                ('newerVersion', models.ForeignKey(related_name='olderVersion', blank=True, to='meta.ControlPoint', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CoordinateSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('objectId', models.CharField(max_length=36, verbose_name=b'Object ID')),
                ('deleted', models.BooleanField(default=False, verbose_name=b'Object deleted')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CoordinateTransform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('objectId', models.CharField(max_length=36, verbose_name=b'Object ID')),
                ('deleted', models.BooleanField(default=False, verbose_name=b'Object deleted')),
                ('transformType', models.CharField(max_length=1, choices=[(b'c', b'Cartesian'), (b's', b'Similarity'), (b'g', b'Geographic')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('history', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('objectId', models.CharField(max_length=36, verbose_name=b'Object ID')),
                ('deleted', models.BooleanField(default=False, verbose_name=b'Object deleted')),
                ('fileFormat', models.CharField(max_length=4)),
                ('pixelFormat', models.CharField(max_length=1, choices=[(b'b', b'int8'), (b'h', b'int16'), (b'i', b'int32'), (b'l', b'int64'), (b'e', b'float16'), (b'f', b'float32'), (b'd', b'float64'), (b'g', b'float128'), (b'B', b'uint8'), (b'H', b'uint16'), (b'I', b'uint32'), (b'L', b'uint64'), (b'F', b'complex64'), (b'D', b'complex128'), (b'G', b'complex256'), (b'?', b'bool'), (b'O', b'object'), (b'S', b'string'), (b'U', b'unicode'), (b'V', b'void')])),
                ('imageWidth', models.PositiveIntegerField(verbose_name=b'Image Width (pixels)')),
                ('imageHeight', models.PositiveIntegerField(verbose_name=b'Image Height (pixels)')),
                ('numberColorBands', models.PositiveIntegerField(verbose_name=b'Number of Color Bands')),
                ('imageUrl', models.TextField()),
                ('originalImageUrl', models.TextField()),
                ('camera', models.ForeignKey(blank=True, to='meta.Camera', null=True)),
                ('newerVersion', models.ForeignKey(related_name='olderVersion', blank=True, to='meta.Image', null=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ImageCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('objectId', models.CharField(max_length=36, verbose_name=b'Object ID')),
                ('deleted', models.BooleanField(default=False, verbose_name=b'Object deleted')),
                ('images', models.ManyToManyField(to='meta.Image')),
                ('newerVersion', models.ForeignKey(related_name='olderVersion', blank=True, to='meta.ImageCollection', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Scene',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('objectId', models.CharField(max_length=36, verbose_name=b'Object ID')),
                ('deleted', models.BooleanField(default=False, verbose_name=b'Object deleted')),
                ('origin', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('geolocated', models.BooleanField(default=True)),
                ('bbox_min', django.contrib.gis.db.models.fields.PointField(default=b'POINT(0 0 0)', srid=4326, dim=3)),
                ('bbox_max', django.contrib.gis.db.models.fields.PointField(default=b'POINT(0 0 0)', srid=4326, dim=3)),
                ('default_voxel_size', django.contrib.gis.db.models.fields.PointField(default=b'POINT(0 0 0)', srid=4326, dim=3)),
                ('newerVersion', models.ForeignKey(related_name='olderVersion', blank=True, to='meta.Scene', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inputs', models.TextField(verbose_name=b'Inputs')),
                ('outputs', models.TextField(verbose_name=b'Outputs')),
                ('user', models.CharField(max_length=32)),
                ('entryTime', models.DateTimeField(auto_now_add=True)),
                ('finishTime', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(max_length=32)),
                ('serviceName', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('xRegion', models.FloatField()),
                ('yRegion', models.FloatField()),
                ('zRegion', models.FloatField()),
                ('name', models.CharField(max_length=32)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TiePoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('objectId', models.CharField(max_length=36, verbose_name=b'Object ID')),
                ('deleted', models.BooleanField(default=False, verbose_name=b'Object deleted')),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('geoPoint', models.ForeignKey(blank=True, to='meta.ControlPoint', null=True)),
                ('image', models.ForeignKey(to='meta.Image')),
                ('newerVersion', models.ForeignKey(related_name='olderVersion', blank=True, to='meta.TiePoint', null=True)),
                ('service', models.ForeignKey(to='meta.ServiceInstance')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VoxelWorld',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('objectId', models.CharField(max_length=36, verbose_name=b'Object ID')),
                ('deleted', models.BooleanField(default=False, verbose_name=b'Object deleted')),
                ('origin', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('voxel_world_dir', models.TextField()),
                ('newerVersion', models.ForeignKey(related_name='olderVersion', blank=True, to='meta.VoxelWorld', null=True)),
                ('service', models.ForeignKey(to='meta.ServiceInstance')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorkflowInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CartesianCoordinateSystem',
            fields=[
                ('coordinatesystem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='meta.CoordinateSystem')),
                ('xUnit', models.CharField(max_length=1, choices=[(b'm', b'Meters'), (b'f', b'Feet')])),
                ('yUnit', models.CharField(max_length=1, choices=[(b'm', b'Meters'), (b'f', b'Feet')])),
                ('zUnit', models.CharField(max_length=1, choices=[(b'm', b'Meters'), (b'f', b'Feet')])),
            ],
            options={
                'abstract': False,
            },
            bases=('meta.coordinatesystem',),
        ),
        migrations.CreateModel(
            name='CartesianTransform',
            fields=[
                ('coordinatetransform_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='meta.CoordinateTransform')),
                ('rodriguezX', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('rodriguezY', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('rodriguezZ', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('translation', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
            ],
            options={
                'abstract': False,
            },
            bases=('meta.coordinatetransform',),
        ),
        migrations.CreateModel(
            name='GeoreferenceCoordinateSystem',
            fields=[
                ('coordinatesystem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='meta.CoordinateSystem')),
                ('xUnit', models.CharField(max_length=1, choices=[(b'm', b'Meters'), (b'f', b'Feet'), (b'r', b'Radians'), (b'd', b'Degrees')])),
                ('yUnit', models.CharField(max_length=1, choices=[(b'm', b'Meters'), (b'f', b'Feet'), (b'r', b'Radians'), (b'd', b'Degrees')])),
                ('zUnit', models.CharField(max_length=1, choices=[(b'm', b'Meters'), (b'f', b'Feet'), (b'r', b'Radians'), (b'd', b'Degrees')])),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
            ],
            options={
                'abstract': False,
            },
            bases=('meta.coordinatesystem',),
        ),
        migrations.AddField(
            model_name='session',
            name='origin',
            field=models.ForeignKey(to='meta.CoordinateSystem'),
        ),
        migrations.AddField(
            model_name='serviceinstance',
            name='workflow',
            field=models.ForeignKey(blank=True, to='meta.WorkflowInstance', null=True),
        ),
        migrations.AddField(
            model_name='scene',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
        migrations.AddField(
            model_name='imagecollection',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
        migrations.AddField(
            model_name='image',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
        migrations.AddField(
            model_name='coordinatetransform',
            name='coordinateSystem_from',
            field=models.ForeignKey(related_name='coordinatetransform_from_set', to='meta.CoordinateSystem'),
        ),
        migrations.AddField(
            model_name='coordinatetransform',
            name='coordinateSystem_to',
            field=models.ForeignKey(related_name='coordinatetransform_to_set', to='meta.CoordinateSystem'),
        ),
        migrations.AddField(
            model_name='coordinatetransform',
            name='newerVersion',
            field=models.ForeignKey(related_name='olderVersion', blank=True, to='meta.CoordinateTransform', null=True),
        ),
        migrations.AddField(
            model_name='coordinatetransform',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
        migrations.AddField(
            model_name='coordinatesystem',
            name='newerVersion',
            field=models.ForeignKey(related_name='olderVersion', blank=True, to='meta.CoordinateSystem', null=True),
        ),
        migrations.AddField(
            model_name='coordinatesystem',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
        migrations.AddField(
            model_name='controlpoint',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
        migrations.AddField(
            model_name='camera',
            name='coordinateSystem',
            field=models.ForeignKey(to='meta.CoordinateSystem'),
        ),
        migrations.AddField(
            model_name='camera',
            name='newerVersion',
            field=models.ForeignKey(related_name='olderVersion', blank=True, to='meta.Camera', null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
    ]
