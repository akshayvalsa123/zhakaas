# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_reporturls'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExhibitorReportUrls',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=500)),
                ('description', models.TextField(null=True, blank=True)),
                ('seq', models.IntegerField(null=True, blank=True)),
                ('exhibitor', models.ForeignKey(to='api.Exhibitor')),
                ('reportUrl', models.ForeignKey(to='api.ReportUrls')),
            ],
            options={
                'db_table': 'ExhibitorReportUrls',
            },
        ),
        migrations.AddField(
            model_name='leaddetails',
            name='comment',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='leaddetails',
            name='rating',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
