# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_reporturls_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reporturls',
            name='tradeshow',
        ),
        migrations.DeleteModel(
            name='ReportUrls',
        ),
    ]
