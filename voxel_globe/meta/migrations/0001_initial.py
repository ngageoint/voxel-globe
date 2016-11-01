# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
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
                ('_attributes', models.TextField(default=b'')),
                ('focal_length', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('principal_point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CameraSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('_attributes', models.TextField(default=b'')),
                ('cameras', models.ManyToManyField(to='meta.Camera')),
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
                ('_attributes', models.TextField(default=b'')),
                ('description', models.TextField()),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('original_point', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3, null=True, blank=True)),
                ('original_srid', models.IntegerField(null=True, blank=True)),
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
                ('_attributes', models.TextField(default=b'')),
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
                ('_attributes', models.TextField(default=b'')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('_attributes', models.TextField(default=b'')),
                ('file_format', models.CharField(max_length=4)),
                ('pixel_format', models.CharField(max_length=1, choices=[(b'b', b'int8'), (b'h', b'int16'), (b'i', b'int32'), (b'l', b'int64'), (b'e', b'float16'), (b'f', b'float32'), (b'd', b'float64'), (b'g', b'float128'), (b'B', b'uint8'), (b'H', b'uint16'), (b'I', b'uint32'), (b'L', b'uint64'), (b'F', b'complex64'), (b'D', b'complex128'), (b'G', b'complex256'), (b'?', b'bool'), (b'O', b'object'), (b'S', b'string'), (b'U', b'unicode'), (b'V', b'void')])),
                ('image_width', models.PositiveIntegerField(verbose_name=b'Image Width (pixels)')),
                ('image_height', models.PositiveIntegerField(verbose_name=b'Image Height (pixels)')),
                ('number_bands', models.PositiveIntegerField(verbose_name=b'Number of Color Bands')),
                ('_filename_path', models.TextField()),
                ('acquisition_date', models.DateTimeField(null=True, blank=True)),
                ('coverage_poly', django.contrib.gis.db.models.fields.PolygonField(srid=4326, null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ImageSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('_attributes', models.TextField(default=b'')),
                ('images', models.ManyToManyField(to='meta.Image')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PointCloud',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('_attributes', models.TextField(default=b'')),
                ('origin', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('_filename_path', models.TextField()),
                ('_potree_dir', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SattelSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('_attributes', models.TextField(default=b'')),
                ('bbox_min', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('bbox_max', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
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
                ('_attributes', models.TextField(default=b'')),
                ('origin', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('geolocated', models.BooleanField(default=True)),
                ('bbox_min', django.contrib.gis.db.models.fields.PointField(default=b'POINT(0 0 0)', srid=4326, dim=3)),
                ('bbox_max', django.contrib.gis.db.models.fields.PointField(default=b'POINT(0 0 0)', srid=4326, dim=3)),
                ('default_voxel_size', django.contrib.gis.db.models.fields.PointField(default=b'POINT(0 0 0)', srid=4326, dim=3)),
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
                ('entry_time', models.DateTimeField(auto_now_add=True)),
                ('finish_time', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(max_length=32)),
                ('service_name', models.CharField(max_length=128)),
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
                ('_attributes', models.TextField(default=b'')),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('control_point', models.ForeignKey(blank=True, to='meta.ControlPoint', null=True)),
                ('image', models.ForeignKey(to='meta.Image')),
                ('service', models.ForeignKey(to='meta.ServiceInstance')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TiePointSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('_attributes', models.TextField(default=b'')),
                ('service', models.ForeignKey(to='meta.ServiceInstance')),
                ('tie_points', models.ManyToManyField(to='meta.TiePoint')),
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
                ('_attributes', models.TextField(default=b'')),
                ('origin', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('directory', models.TextField()),
                ('service', models.ForeignKey(to='meta.ServiceInstance')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CartesianCoordinateSystem',
            fields=[
                ('coordinatesystem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='meta.CoordinateSystem')),
                ('x_unit', models.CharField(max_length=1, choices=[(b'm', b'Meters'), (b'f', b'Feet')])),
                ('y_unit', models.CharField(max_length=1, choices=[(b'm', b'Meters'), (b'f', b'Feet')])),
                ('z_unit', models.CharField(max_length=1, choices=[(b'm', b'Meters'), (b'f', b'Feet')])),
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
                ('x_unit', models.CharField(max_length=1, choices=[(b'm', b'Meters'), (b'f', b'Feet'), (b'r', b'Radians'), (b'd', b'Degrees')])),
                ('y_unit', models.CharField(max_length=1, choices=[(b'm', b'Meters'), (b'f', b'Feet'), (b'r', b'Radians'), (b'd', b'Degrees')])),
                ('z_unit', models.CharField(max_length=1, choices=[(b'm', b'Meters'), (b'f', b'Feet'), (b'r', b'Radians'), (b'd', b'Degrees')])),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
            ],
            options={
                'abstract': False,
            },
            bases=('meta.coordinatesystem',),
        ),
        migrations.AddField(
            model_name='scene',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
        migrations.AddField(
            model_name='sattelsite',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
        migrations.AddField(
            model_name='pointcloud',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
        migrations.AddField(
            model_name='imageset',
            name='scene',
            field=models.ForeignKey(blank=True, to='meta.Scene', null=True),
        ),
        migrations.AddField(
            model_name='imageset',
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
            name='coordinate_system_from',
            field=models.ForeignKey(related_name='coordinatetransform_from_set', to='meta.CoordinateSystem'),
        ),
        migrations.AddField(
            model_name='coordinatetransform',
            name='coordinate_system_to',
            field=models.ForeignKey(related_name='coordinatetransform_to_set', to='meta.CoordinateSystem'),
        ),
        migrations.AddField(
            model_name='coordinatetransform',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
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
            model_name='cameraset',
            name='images',
            field=models.ForeignKey(related_name='cameras', to='meta.ImageSet'),
        ),
        migrations.AddField(
            model_name='cameraset',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
        migrations.AddField(
            model_name='camera',
            name='coordinate_system',
            field=models.ForeignKey(to='meta.CoordinateSystem'),
        ),
        migrations.AddField(
            model_name='camera',
            name='image',
            field=models.ForeignKey(to='meta.Image'),
        ),
        migrations.AddField(
            model_name='camera',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
    ]
