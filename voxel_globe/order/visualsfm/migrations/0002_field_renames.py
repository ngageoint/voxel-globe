# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0013_field_renames'),
        ('order.visualsfm', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='imageCollection',
        ),
        migrations.AddField(
            model_name='order',
            name='imageSet',
            field=models.ForeignKey(default=1, to='meta.ImageSet'),
            preserve_default=False,
        ),
    ]
