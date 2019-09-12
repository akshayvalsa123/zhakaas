# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('address1', models.TextField()),
                ('address2', models.TextField(null=True, blank=True)),
                ('street', models.CharField(max_length=100, null=True, blank=True)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('zipcode', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'Address',
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'Answer',
            },
        ),
        migrations.CreateModel(
            name='DeviceDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deviceName', models.CharField(max_length=300)),
                ('deviceModel', models.CharField(max_length=100)),
                ('appVersion', models.CharField(max_length=30)),
                ('isActive', models.BooleanField()),
                ('initTime', models.DateTimeField()),
                ('syncTime', models.DateTimeField()),
            ],
            options={
                'db_table': 'DeviceDetails',
            },
        ),
        migrations.CreateModel(
            name='Exhibitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('contactNo', models.CharField(max_length=30)),
                ('alternateEmail', models.EmailField(max_length=254, null=True, blank=True)),
                ('alternateContactNo', models.CharField(max_length=30, null=True, blank=True)),
                ('licenseCount', models.IntegerField()),
                ('address', models.ForeignKey(to='api.Address')),
            ],
            options={
                'db_table': 'Exhibitor',
            },
        ),
        migrations.CreateModel(
            name='ExhibitorBooth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('contactNo', models.CharField(max_length=30)),
                ('boothNo', models.CharField(max_length=30, null=True, blank=True)),
                ('exhibitor', models.ForeignKey(to='api.Exhibitor')),
            ],
            options={
                'db_table': 'ExhibitorBooth',
            },
        ),
        migrations.CreateModel(
            name='ExhibitorSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('settingValue', models.TextField()),
                ('defaultSettingValue', models.CharField(max_length=100)),
                ('exhibitor', models.ForeignKey(to='api.Exhibitor')),
            ],
            options={
                'db_table': 'ExhibitorSettings',
            },
        ),
        migrations.CreateModel(
            name='Fields',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'Fields',
            },
        ),
        migrations.CreateModel(
            name='FieldsMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('fieldSeq', models.IntegerField()),
                ('isUnique', models.BooleanField()),
                ('field', models.ForeignKey(to='api.Fields')),
            ],
            options={
                'db_table': 'FieldsMapping',
            },
        ),
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'Industry',
            },
        ),
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'Lead',
            },
        ),
        migrations.CreateModel(
            name='LeadDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('scanType', models.CharField(max_length=100)),
                ('syncID', models.CharField(max_length=100)),
                ('captureTime', models.DateTimeField()),
                ('lookupStatus', models.CharField(max_length=100)),
                ('leadSyncStatus', models.CharField(max_length=100)),
                ('leadType', models.CharField(max_length=100)),
                ('device', models.ForeignKey(to='api.DeviceDetails')),
            ],
            options={
                'db_table': 'LeadDetails',
            },
        ),
        migrations.CreateModel(
            name='LeadFields',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('fieldValue', models.TextField(null=True, blank=True)),
                ('field', models.ForeignKey(to='api.Fields')),
            ],
            options={
                'db_table': 'LeadFields',
            },
        ),
        migrations.CreateModel(
            name='LeadMaster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('leadID', models.CharField(max_length=100)),
                ('leadFields', models.ManyToManyField(to='api.Fields', through='api.LeadFields')),
            ],
            options={
                'db_table': 'LeadMaster',
            },
        ),
        migrations.CreateModel(
            name='Mapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('totalFields', models.IntegerField()),
                ('badgeIDFieldSeq', models.IntegerField()),
                ('badgeDataFieldSeq', models.IntegerField()),
                ('fields', models.ManyToManyField(to='api.Fields', through='api.FieldsMapping')),
            ],
            options={
                'db_table': 'Mapping',
            },
        ),
        migrations.CreateModel(
            name='Qualifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('qualifierName', models.CharField(max_length=300)),
                ('screenNo', models.IntegerField()),
                ('ansFormat', models.IntegerField()),
                ('totalQuestions', models.IntegerField()),
                ('exhibitor', models.ForeignKey(to='api.Exhibitor')),
            ],
            options={
                'db_table': 'Qualifier',
            },
        ),
        migrations.CreateModel(
            name='QualifierQuestions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('seq', models.IntegerField()),
                ('qualifier', models.ForeignKey(to='api.Qualifier')),
            ],
            options={
                'db_table': 'QualifierQuestions',
            },
        ),
        migrations.CreateModel(
            name='QualifierType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('qualifierType', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'QualifierType',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('question', models.TextField()),
                ('widgetName', models.CharField(max_length=100)),
                ('options', models.CharField(max_length=300)),
            ],
            options={
                'db_table': 'Question',
            },
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('settingType', models.CharField(max_length=100)),
                ('settingName', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'Settings',
            },
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'Sponsor',
            },
        ),
        migrations.CreateModel(
            name='Tradeshow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('nameCode', models.CharField(max_length=10, null=True, blank=True)),
                ('startDate', models.DateTimeField()),
                ('endDate', models.DateTimeField()),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('contactNo', models.CharField(max_length=30)),
                ('adminPassword', models.CharField(max_length=100)),
                ('supportMessage', models.TextField(null=True, blank=True)),
                ('website', models.CharField(max_length=300, null=True, blank=True)),
                ('timeZone', models.CharField(max_length=30, null=True, blank=True)),
                ('address', models.ForeignKey(to='api.Address')),
                ('industry', models.ForeignKey(blank=True, to='api.Industry', null=True)),
                ('sponsors', models.ManyToManyField(to='api.Sponsor', null=True, blank=True)),
            ],
            options={
                'db_table': 'Tradeshow',
            },
        ),
        migrations.CreateModel(
            name='UserLogin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('userName', models.CharField(unique=True, max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('isActive', models.BooleanField()),
            ],
            options={
                'db_table': 'UserLogin',
            },
        ),
        migrations.AddField(
            model_name='qualifierquestions',
            name='question',
            field=models.ForeignKey(to='api.Question'),
        ),
        migrations.AddField(
            model_name='qualifier',
            name='qualifierTypeID',
            field=models.ForeignKey(to='api.QualifierType'),
        ),
        migrations.AddField(
            model_name='qualifier',
            name='questions',
            field=models.ManyToManyField(to='api.Question', through='api.QualifierQuestions'),
        ),
        migrations.AddField(
            model_name='mapping',
            name='tradeshow',
            field=models.ForeignKey(to='api.Tradeshow'),
        ),
        migrations.AddField(
            model_name='leadmaster',
            name='tradeshow',
            field=models.ForeignKey(to='api.Tradeshow'),
        ),
        migrations.AddField(
            model_name='leadfields',
            name='lead',
            field=models.ForeignKey(to='api.LeadMaster'),
        ),
        migrations.AddField(
            model_name='lead',
            name='answers',
            field=models.ManyToManyField(to='api.QualifierQuestions', through='api.Answer'),
        ),
        migrations.AddField(
            model_name='lead',
            name='exhibitorBooth',
            field=models.ForeignKey(to='api.ExhibitorBooth'),
        ),
        migrations.AddField(
            model_name='lead',
            name='leadDetails',
            field=models.ForeignKey(to='api.LeadDetails'),
        ),
        migrations.AddField(
            model_name='lead',
            name='leadMaster',
            field=models.ForeignKey(to='api.LeadMaster'),
        ),
        migrations.AddField(
            model_name='fieldsmapping',
            name='mapping',
            field=models.ForeignKey(to='api.Mapping'),
        ),
        migrations.AddField(
            model_name='exhibitorsettings',
            name='setting',
            field=models.ForeignKey(to='api.Settings'),
        ),
        migrations.AddField(
            model_name='exhibitorbooth',
            name='userName',
            field=models.ForeignKey(to='api.UserLogin'),
        ),
        migrations.AddField(
            model_name='exhibitor',
            name='settings',
            field=models.ManyToManyField(to='api.Settings', through='api.ExhibitorSettings'),
        ),
        migrations.AddField(
            model_name='exhibitor',
            name='tradeshow',
            field=models.ForeignKey(to='api.Tradeshow'),
        ),
        migrations.AddField(
            model_name='answer',
            name='lead',
            field=models.ForeignKey(to='api.Lead'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(to='api.QualifierQuestions'),
        ),
    ]
