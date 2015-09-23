# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0003_fixed_typo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='directory',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='directory',
            name='session',
        ),
        migrations.RemoveField(
            model_name='file',
            name='directory',
        ),
        migrations.AddField(
            model_name='file',
            name='session',
            field=models.ForeignKey(related_name='file', default=1, to='ingest.UploadSession'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Directory',
        ),
    ]
