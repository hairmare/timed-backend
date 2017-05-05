# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-05-01 13:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0003_auto_20170324_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='activity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports', to='tracking.Activity'),
        ),
    ]