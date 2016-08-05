# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0007_sattel_event_trigger_polygon'),
    ]

    operations = [
        migrations.AddField(
            model_name='satteleventtrigger',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sattelgeometryobject',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
    ]
