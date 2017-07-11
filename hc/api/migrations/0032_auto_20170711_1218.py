# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-11 12:18
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_merge_20170711_1147'),
    ]

    operations = [
        migrations.AddField(
            model_name='check',
            name='nag',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='check',
            name='nag_time',
            field=models.DurationField(default=datetime.timedelta(0, 3600)),
        ),
        migrations.AlterField(
            model_name='priority',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'),
                                            ('contacted', 'Contacted')], default='pending',
                                   max_length=100),
        ),
    ]
