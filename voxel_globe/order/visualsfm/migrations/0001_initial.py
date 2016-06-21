# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('processingDir', models.TextField()),
                ('lvcsOrigin', models.TextField()),
                ('imageSet', models.ForeignKey(to='meta.ImageSet')),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(max_length=36)),
                ('startTime', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(related_name='order_order_visualsfm_session_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
