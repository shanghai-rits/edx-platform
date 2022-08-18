# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facet', '0002_auto_20190123_2213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupoflanguage',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_langs', to='facet.Group'),
        ),
    ]
