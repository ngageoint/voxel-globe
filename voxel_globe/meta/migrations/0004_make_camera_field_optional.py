# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0003_event_trigger'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='focal_length',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='camera',
            name='principal_point',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True),
        ),
    ]
