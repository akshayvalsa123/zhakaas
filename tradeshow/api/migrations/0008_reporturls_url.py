# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_reporturls'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporturls',
            name='url',
            field=models.TextField(null=True, blank=True),
        ),
    ]
