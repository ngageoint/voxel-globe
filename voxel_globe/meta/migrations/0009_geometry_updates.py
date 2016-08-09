# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0008_sattel_event_trigger_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sattelgeometryobject',
            name='geometry',
            field=django.contrib.gis.db.models.fields.PolygonField(default=b'POLYGON((0 0 0, 0 0 0, 0 0 0, 0 0 0))', srid=4326, dim=3),
        ),
        migrations.AlterField(
            model_name='sattelgeometryobject',
            name='geometry_path',
            field=models.TextField(null=True, verbose_name=b'Geometry Filename', blank=True),
        ),
    ]
