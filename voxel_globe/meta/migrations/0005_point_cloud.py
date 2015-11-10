# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0004_null_scene_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='PointCloud',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('objectId', models.CharField(max_length=36, verbose_name=b'Object ID')),
                ('deleted', models.BooleanField(default=False, verbose_name=b'Object deleted')),
                ('origin', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('directory', models.TextField()),
                ('newerVersion', models.ForeignKey(related_name='olderVersion', blank=True, to='meta.PointCloud', null=True)),
                ('service', models.ForeignKey(to='meta.ServiceInstance')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameField(
            model_name='voxelworld',
            old_name='voxel_world_dir',
            new_name='directory',
        ),
    ]
