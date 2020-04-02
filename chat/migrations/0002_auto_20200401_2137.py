# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2020-04-01 21:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('handle', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='room',
            name='locked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='player',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='chat.Room'),
        ),
    ]