# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage_setting', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='bannersetting',
            table='homepage_banner_setting',
        ),
    ]
