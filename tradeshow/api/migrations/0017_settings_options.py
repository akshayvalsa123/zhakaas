# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20171225_0023'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='options',
            field=models.CharField(max_length=300, null=True, blank=True),
        ),
    ]
