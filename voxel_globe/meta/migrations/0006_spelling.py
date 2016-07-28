# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0005_add_one_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='satteleventresult',
            name='reference_image',
            field=models.ForeignKey(related_name='reference_event_result', to='meta.Image'),
        ),
    ]
