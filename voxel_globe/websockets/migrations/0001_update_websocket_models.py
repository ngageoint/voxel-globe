# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogMessageModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message_text', models.TextField()),
                ('message_type', models.CharField(max_length=1, choices=[(b'd', b'Debug'), (b'i', b'Info'), (b'w', b'Warn'), (b'e', b'Error'), (b'f', b'Fatal'), (b'm', b'Message')])),
                ('task_id', models.IntegerField()),
            ],
        ),
    ]
