# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0017_point_cloud_filename'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pointcloud',
            old_name='potree_url',
            new_name='_potree_dir',
        ),
    ]
