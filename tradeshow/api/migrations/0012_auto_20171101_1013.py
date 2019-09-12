# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20171101_1011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exhibitorreporturls',
            name='exhibitor',
        ),
        migrations.RemoveField(
            model_name='exhibitorreporturls',
            name='reportUrl',
        ),
        migrations.DeleteModel(
            name='ExhibitorReportUrls',
        ),
    ]
