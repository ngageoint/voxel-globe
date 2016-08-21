# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('websockets', '0003_websocket_log_message_owner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='logmessage',
            old_name='owner2',
            new_name='owner',
        ),
        migrations.AddField(
            model_name='logmessage',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
