# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_userloginsession'),
    ]

    operations = [
        migrations.AddField(
            model_name='userloginsession',
            name='comment',
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userloginsession',
            name='specialLogin',
            field=models.BooleanField(default=False),
        ),
    ]
