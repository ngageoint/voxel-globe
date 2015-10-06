# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0004_remove_ingest_dir'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uploadsession',
            old_name='image_sequence_type',
            new_name='payload_type',
        ),
    ]
