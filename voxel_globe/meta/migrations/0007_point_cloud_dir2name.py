# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0006_potree_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pointcloud',
            old_name='directory',
            new_name='filename',
        ),
    ]
