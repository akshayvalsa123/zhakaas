# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20171101_1013'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLoginSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('authToken', models.CharField(max_length=250)),
                ('loginTime', models.DateTimeField(auto_now_add=True)),
                ('logoutTime', models.DateTimeField(null=True, blank=True)),
                ('user', models.ForeignKey(to='api.UserLogin')),
            ],
            options={
                'db_table': 'UserLoginSession',
            },
        ),
    ]
