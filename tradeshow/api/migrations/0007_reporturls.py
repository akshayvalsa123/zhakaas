# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20170904_2327'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportUrls',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('tradeshow', models.ForeignKey(to='api.Tradeshow')),
            ],
            options={
                'db_table': 'ReportUrls',
            },
        ),
    ]
