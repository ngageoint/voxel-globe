# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0012_reverse_camera_image_relation'),
    ]

    operations = [
        migrations.CreateModel(
            name='CameraSet',
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
            name='ImageSet',
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
            name='TiePointSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('_attributes', models.TextField(default=b'')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='imagecollection',
            name='images',
        ),
        migrations.RemoveField(
            model_name='imagecollection',
            name='scene',
        ),
        migrations.RemoveField(
            model_name='imagecollection',
            name='service',
        ),
        migrations.RemoveField(
            model_name='session',
            name='origin',
        ),
        migrations.RenameField(
            model_name='camera',
            old_name='coordinateSystem',
            new_name='coordinate_system',
        ),
        migrations.RenameField(
            model_name='cartesiancoordinatesystem',
            old_name='xUnit',
            new_name='x_unit',
        ),
        migrations.RenameField(
            model_name='cartesiancoordinatesystem',
            old_name='yUnit',
            new_name='y_unit',
        ),
        migrations.RenameField(
            model_name='cartesiancoordinatesystem',
            old_name='zUnit',
            new_name='z_unit',
        ),
        migrations.RenameField(
            model_name='controlpoint',
            old_name='apparentPoint',
            new_name='original_point',
        ),
        migrations.RenameField(
            model_name='coordinatetransform',
            old_name='coordinateSystem_from',
            new_name='coordinate_system_from',
        ),
        migrations.RenameField(
            model_name='coordinatetransform',
            old_name='coordinateSystem_to',
            new_name='coordinate_system_to',
        ),
        migrations.RenameField(
            model_name='georeferencecoordinatesystem',
            old_name='xUnit',
            new_name='x_unit',
        ),
        migrations.RenameField(
            model_name='georeferencecoordinatesystem',
            old_name='yUnit',
            new_name='y_unit',
        ),
        migrations.RenameField(
            model_name='georeferencecoordinatesystem',
            old_name='zUnit',
            new_name='z_unit',
        ),
        migrations.RenameField(
            model_name='image',
            old_name='fileFormat',
            new_name='file_format',
        ),
        migrations.RenameField(
            model_name='image',
            old_name='imageHeight',
            new_name='image_height',
        ),
        migrations.RenameField(
            model_name='image',
            old_name='imageWidth',
            new_name='image_width',
        ),
        migrations.RenameField(
            model_name='image',
            old_name='numberColorBands',
            new_name='number_bands',
        ),
        migrations.RenameField(
            model_name='image',
            old_name='originalImageUrl',
            new_name='original_image_url',
        ),
        migrations.RenameField(
            model_name='image',
            old_name='pixelFormat',
            new_name='pixel_format',
        ),
        migrations.RenameField(
            model_name='serviceinstance',
            old_name='entryTime',
            new_name='entry_time',
        ),
        migrations.RenameField(
            model_name='serviceinstance',
            old_name='finishTime',
            new_name='finish_time',
        ),
        migrations.RenameField(
            model_name='serviceinstance',
            old_name='serviceName',
            new_name='service_name',
        ),
        migrations.RenameField(
            model_name='tiepoint',
            old_name='geoPoint',
            new_name='control_point',
        ),
        migrations.RemoveField(
            model_name='camera',
            name='focalLengthU',
        ),
        migrations.RemoveField(
            model_name='camera',
            name='focalLengthV',
        ),
        migrations.RemoveField(
            model_name='camera',
            name='principalPointU',
        ),
        migrations.RemoveField(
            model_name='camera',
            name='principalPointV',
        ),
        migrations.RemoveField(
            model_name='coordinatetransform',
            name='transformType',
        ),
        migrations.RemoveField(
            model_name='image',
            name='imageUrl',
        ),
        migrations.AddField(
            model_name='camera',
            name='focal_length',
            field=django.contrib.gis.db.models.fields.PointField(default='POINT(0 0)', srid=4326),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='camera',
            name='principal_point',
            field=django.contrib.gis.db.models.fields.PointField(default='POINT(0 0)', srid=4326),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='controlpoint',
            name='original_srid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='image',
            name='image_url',
            field=models.TextField(default='', unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='camera',
            name='image',
            field=models.ForeignKey(to='meta.Image'),
        ),
    ]
