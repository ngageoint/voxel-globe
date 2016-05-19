# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0010_remove_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlpoint',
            name='_attributes',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='coordinatesystem',
            name='_attributes',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='coordinatetransform',
            name='_attributes',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='image',
            name='_attributes',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='imagecollection',
            name='_attributes',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='pointcloud',
            name='_attributes',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='scene',
            name='_attributes',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='tiepoint',
            name='_attributes',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='voxelworld',
            name='_attributes',
            field=models.TextField(default=b''),
        ),
    ]
