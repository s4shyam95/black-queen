# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-04-03 08:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_auto_20200403_0553'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='player',
            options={'ordering': ['timestamp']},
        ),
        migrations.AddField(
            model_name='player',
            name='timestamp',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
