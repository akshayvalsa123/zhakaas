# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TradeshowSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('settingValue', models.TextField()),
                ('defaultSettingValue', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'TradeshowSettings',
            },
        ),
        migrations.RemoveField(
            model_name='exhibitorsettings',
            name='exhibitor',
        ),
        migrations.RemoveField(
            model_name='exhibitorsettings',
            name='setting',
        ),
        migrations.RemoveField(
            model_name='exhibitor',
            name='settings',
        ),
        migrations.AddField(
            model_name='settings',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='settings',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.DeleteModel(
            name='ExhibitorSettings',
        ),
        migrations.AddField(
            model_name='tradeshowsettings',
            name='setting',
            field=models.ForeignKey(to='api.Settings'),
        ),
        migrations.AddField(
            model_name='tradeshowsettings',
            name='tradeshow',
            field=models.ForeignKey(to='api.Tradeshow'),
        ),
        migrations.AddField(
            model_name='tradeshow',
            name='settings',
            field=models.ManyToManyField(to='api.Settings', through='api.TradeshowSettings'),
        ),
    ]
