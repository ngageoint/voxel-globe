# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0013_field_renames'),
        ('order.visualsfm', '0002_field_renames'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ImageCollection',
        ),
        migrations.DeleteModel(
            name='Session',
        ),
        migrations.AddField(
            model_name='tiepointset',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
        migrations.AddField(
            model_name='tiepointset',
            name='tie_points',
            field=models.ManyToManyField(to='meta.TiePoint'),
        ),
        migrations.AddField(
            model_name='imageset',
            name='images',
            field=models.ManyToManyField(to='meta.Image'),
        ),
        migrations.AddField(
            model_name='imageset',
            name='scene',
            field=models.ForeignKey(blank=True, to='meta.Scene', null=True),
        ),
        migrations.AddField(
            model_name='imageset',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
        migrations.AddField(
            model_name='cameraset',
            name='cameras',
            field=models.ManyToManyField(to='meta.Camera'),
        ),
        migrations.AddField(
            model_name='cameraset',
            name='images',
            field=models.ForeignKey(related_name='cameras', to='meta.ImageSet'),
        ),
        migrations.AddField(
            model_name='cameraset',
            name='service',
            field=models.ForeignKey(to='meta.ServiceInstance'),
        ),
    ]
