# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-22 06:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zilencer', '0012_coupon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='billing_user',
        ),
    ]
