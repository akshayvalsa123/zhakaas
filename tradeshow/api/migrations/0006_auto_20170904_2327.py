# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_devicedetails_deviceid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaddetails',
            name='device',
            field=models.ForeignKey(blank=True, to='api.DeviceDetails', null=True),
        ),
    ]
