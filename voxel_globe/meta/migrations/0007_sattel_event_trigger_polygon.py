# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0006_spelling'),
    ]

    operations = [
        migrations.AddField(
            model_name='sattelgeometryobject',
            name='geometry',
            field=django.contrib.gis.db.models.fields.PolygonField(default='POLYGON((0 0 0, 0 0 0, 0 0 0, 0 0 0))', srid=4326, dim=3),
            preserve_default=False,
        ),
    ]
