# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0002_optional_serivce_instance'),
    ]

    operations = [
        migrations.CreateModel(
            name='RpcCamera',
            fields=[
                ('camera_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='meta.Camera')),
                ('rpc_path', models.TextField(verbose_name=b'Geometry Filename')),
            ],
            options={
                'abstract': False,
            },
            bases=('meta.camera',),
        ),
        migrations.CreateModel(
            name='SattelEventResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('_attributes', models.TextField(default=b'')),
                ('score', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SattelEventTrigger',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('_attributes', models.TextField(default=b'')),
                ('origin', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SattelGeometryObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('_attributes', models.TextField(default=b'')),
                ('origin', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('geometry_path', models.TextField(verbose_name=b'Geometry Filename')),
                ('service', models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='sattelsite',
            name='camera_set',
            field=models.ForeignKey(to='meta.CameraSet', null=True),
        ),
        migrations.AddField(
            model_name='sattelsite',
            name='image_set',
            field=models.ForeignKey(to='meta.ImageSet', null=True),
        ),
        migrations.AddField(
            model_name='sattelgeometryobject',
            name='site',
            field=models.ForeignKey(to='meta.SattelSite'),
        ),
        migrations.AddField(
            model_name='satteleventtrigger',
            name='event_areas',
            field=models.ManyToManyField(related_name='event_event_trigger', to='meta.SattelGeometryObject'),
        ),
        migrations.AddField(
            model_name='satteleventtrigger',
            name='reference_areas',
            field=models.ManyToManyField(related_name='reference_event_trigger', to='meta.SattelGeometryObject'),
        ),
        migrations.AddField(
            model_name='satteleventtrigger',
            name='reference_image',
            field=models.ForeignKey(to='meta.Image'),
        ),
        migrations.AddField(
            model_name='satteleventtrigger',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AddField(
            model_name='satteleventtrigger',
            name='site',
            field=models.ForeignKey(to='meta.SattelSite'),
        ),
        migrations.AddField(
            model_name='satteleventresult',
            name='geometry',
            field=models.ForeignKey(to='meta.SattelGeometryObject'),
        ),
        migrations.AddField(
            model_name='satteleventresult',
            name='mission_image',
            field=models.ForeignKey(related_name='mission_event_result', to='meta.Image'),
        ),
        migrations.AddField(
            model_name='satteleventresult',
            name='reference_image',
            field=models.ForeignKey(related_name='referenve_event_result', to='meta.Image'),
        ),
        migrations.AddField(
            model_name='satteleventresult',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
    ]
