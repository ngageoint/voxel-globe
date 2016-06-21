# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0018_potree_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='SattelSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('_attributes', models.TextField(default=b'')),
                ('bbox_min', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3, geography=True)),
                ('bbox_max', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3, geography=True)),
                ('service', models.ForeignKey(to='meta.ServiceInstance')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
