# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(max_length=36)),
                ('startTime', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(related_name='order_build_voxel_world_session_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
