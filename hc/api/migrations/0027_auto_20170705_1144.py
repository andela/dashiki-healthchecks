# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-05 11:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0026_auto_20160415_1824'),
    ]

    operations = [
        migrations.CreateModel(
            name='Priority',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(choices=[(1, 'High'), (2, 'Medium'), (3, 'Low')], max_length=1)),
                ('enabled', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('contacted', 'Contacted'), ('unresponsive', 'Unresponsive'), ('responded', 'Responded')], default='pending', max_length=100)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Check')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='channel',
            name='kind',
            field=models.CharField(choices=[('email', 'Email'), ('webhook', 'Webhook'), ('hipchat', 'HipChat'), ('slack', 'Slack'), ('pd', 'PagerDuty'), ('po', 'Pushover'), ('victorops', 'VictorOps'), ('pushbullet', 'PushBullet')], max_length=20),
        ),
    ]