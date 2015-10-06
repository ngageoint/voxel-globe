# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadsession',
            name='metadata_type',
            field=models.CharField(default='None', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='uploadsession',
            name='video_type',
            field=models.CharField(default='None', max_length=30),
            preserve_default=False,
        ),
    ]
