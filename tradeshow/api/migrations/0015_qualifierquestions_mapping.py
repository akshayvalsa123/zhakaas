# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20171215_0007'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualifierquestions',
            name='mapping',
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
    ]
