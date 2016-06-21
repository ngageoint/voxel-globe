# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0019_sattel_site_add'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sattelsite',
            name='service',
        ),
        migrations.DeleteModel(
            name='SattelSite',
        ),
    ]
