# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AlterField(
            model_name='cameraset',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AlterField(
            model_name='controlpoint',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AlterField(
            model_name='coordinatesystem',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AlterField(
            model_name='coordinatetransform',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AlterField(
            model_name='imageset',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AlterField(
            model_name='pointcloud',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AlterField(
            model_name='sattelsite',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AlterField(
            model_name='scene',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AlterField(
            model_name='tiepoint',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AlterField(
            model_name='tiepointset',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
        migrations.AlterField(
            model_name='voxelworld',
            name='service',
            field=models.ForeignKey(blank=True, to='meta.ServiceInstance', null=True),
        ),
    ]
