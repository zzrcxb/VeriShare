# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-03 19:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pshare', '0002_userfile_alias'),
    ]

    operations = [
        migrations.AddField(
            model_name='userfile',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]