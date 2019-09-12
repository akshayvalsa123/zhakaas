# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20170808_1308'),
    ]

    operations = [
        migrations.AddField(
            model_name='fields',
            name='displayName',
            field=models.CharField(default='test', max_length=100),
            preserve_default=False,
        ),
    ]
