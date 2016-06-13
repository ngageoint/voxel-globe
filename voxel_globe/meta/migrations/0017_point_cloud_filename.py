# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0016_image_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='pointcloud',
            name='_filename_path',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
