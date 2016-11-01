# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0004_make_camera_field_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='coordinate_system',
            field=models.ForeignKey(blank=True, to='meta.CoordinateSystem', null=True),
        ),
    ]
