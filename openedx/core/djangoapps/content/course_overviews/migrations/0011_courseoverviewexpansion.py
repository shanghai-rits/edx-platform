# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0010_auto_20160329_2317'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseOverviewExpansion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_overview', models.CharField(max_length=255)),
                ('chinese_display_name', models.TextField(null=True)),
                ('vertical_cover_path', models.TextField(default=b'', blank=True)),
            ],
        ),
    ]
