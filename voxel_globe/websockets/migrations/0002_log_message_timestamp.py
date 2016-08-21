# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('websockets', '0001_update_websocket_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='logmessagemodel',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 16, 12, 54, 35, 276042, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
