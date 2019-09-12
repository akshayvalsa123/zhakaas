# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20170808_1205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradeshowsettings',
            name='defaultSettingValue',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
