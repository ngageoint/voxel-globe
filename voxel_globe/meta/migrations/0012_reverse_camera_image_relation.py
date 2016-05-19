# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0011_added_attributes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='camera',
        ),
        migrations.AddField(
            model_name='camera',
            name='image',
            field=models.ForeignKey(blank=True, to='meta.Image', null=True),
        ),
    ]
