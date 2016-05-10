# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0007_point_cloud_dir2name'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='_attributes',
            field=models.TextField(default=b''),
        ),
    ]
