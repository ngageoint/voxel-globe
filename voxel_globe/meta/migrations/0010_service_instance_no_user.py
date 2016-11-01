# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0009_geometry_updates'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceinstance',
            name='user',
        ),
    ]
