# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0003_scene_key_imagecollection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagecollection',
            name='scene',
            field=models.ForeignKey(blank=True, to='meta.Scene', null=True),
        ),
    ]
