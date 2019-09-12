# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_qualifierquestions_mapping'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=300)),
            ],
        ),
        migrations.RemoveField(
            model_name='devicedetails',
            name='appVersion',
        ),
        migrations.RemoveField(
            model_name='devicedetails',
            name='deviceModel',
        ),
        migrations.RemoveField(
            model_name='devicedetails',
            name='deviceName',
        ),
        migrations.RemoveField(
            model_name='leaddetails',
            name='device',
        ),
        migrations.AddField(
            model_name='devicedetails',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='devicedetails',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='userSession',
            field=models.ForeignKey(blank=True, to='api.UserLoginSession', null=True),
        ),
        migrations.AddField(
            model_name='userloginsession',
            name='device',
            field=models.ForeignKey(blank=True, to='api.DeviceDetails', null=True),
        ),
        migrations.AlterField(
            model_name='devicedetails',
            name='initTime',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='devicedetails',
            name='syncTime',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='devicedetails',
            name='deviceFields',
            field=models.ManyToManyField(to='api.DeviceField'),
        ),
    ]
