# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20171014_0824'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportUrls',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=500)),
                ('url', models.TextField()),
                ('description', models.TextField(null=True, blank=True)),
                ('seq', models.IntegerField(null=True, blank=True)),
                ('tradeshow', models.ForeignKey(to='api.Tradeshow')),
            ],
            options={
                'db_table': 'ReportUrls',
            },
        ),
    ]
