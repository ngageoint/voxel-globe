# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0015_ununique'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='original_filename',
            new_name='_filename_path',
        ),
        migrations.RemoveField(
            model_name='image',
            name='image_url',
        ),
        migrations.RemoveField(
            model_name='image',
            name='original_image_url',
        ),
        migrations.RemoveField(
            model_name='pointcloud',
            name='filename',
        ),
    ]
