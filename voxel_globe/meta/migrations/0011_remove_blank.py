# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0010_add_height'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sattelgeometryobject',
            name='height',
            field=models.FloatField(default=0.0),
        ),
    ]
