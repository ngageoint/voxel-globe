# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0002_auto_20150917_2050'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uploadsession',
            old_name='video_type',
            new_name='image_sequence_type',
        ),
    ]
