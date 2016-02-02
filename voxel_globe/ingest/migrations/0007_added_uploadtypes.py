# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0006_upload_cleanup'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadsession',
            name='upload_types',
            field=models.TextField(default=b'{}'),
        ),
    ]
