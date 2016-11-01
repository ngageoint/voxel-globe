# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('websockets', '0002_log_message_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message_text', models.TextField()),
                ('message_type', models.CharField(max_length=1, choices=[(b'd', b'Debug'), (b'i', b'Info'), (b'w', b'Warn'), (b'e', b'Error'), (b'f', b'Fatal'), (b'm', b'Message')])),
                ('task_id', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('owner2', models.ForeignKey(related_name='websockets_log_message_owner', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='LogMessageModel',
        ),
    ]
