# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0005_rename_payload'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadsession',
            name='sensorType',
        ),
    ]
