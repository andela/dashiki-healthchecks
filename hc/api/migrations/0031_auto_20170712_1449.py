# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-12 14:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_auto_20170710_0854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='priority',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('contacted', 'Contacted')], default='pending', max_length=100),
        ),
    ]