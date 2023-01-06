# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0011_courseoverviewexpansion'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverviewexpansion',
            name='eng_display_name',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
