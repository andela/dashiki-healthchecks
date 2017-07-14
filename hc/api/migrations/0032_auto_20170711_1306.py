# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-11 13:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_merge_20170711_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='priority',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('contacted', 'Contacted')], default='pending', max_length=100),
        ),
    ]
