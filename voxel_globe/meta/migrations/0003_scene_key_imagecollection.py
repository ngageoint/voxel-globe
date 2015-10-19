# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0002_add_original_filename_to_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagecollection',
            name='scene',
            field=models.ForeignKey(default=15, to='meta.Scene'),
            preserve_default=False,
        ),
    ]
