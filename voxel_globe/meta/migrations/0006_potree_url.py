# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0005_point_cloud'),
    ]

    operations = [
        migrations.AddField(
            model_name='pointcloud',
            name='potree_url',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
