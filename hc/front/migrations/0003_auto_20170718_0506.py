# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-18 05:06
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0002_auto_20170718_0503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faqitem',
            name='body',
            field=ckeditor.fields.RichTextField(max_length=2000),
        ),
    ]
