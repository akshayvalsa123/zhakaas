# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_fields_displayname'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicedetails',
            name='deviceID',
            field=models.CharField(default='d1', max_length=100),
            preserve_default=False,
        ),
    ]
