# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RecommendedCourses',
            fields=[
                ('unicodecoursekey', models.CharField(max_length=100, serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'recommended_courses',
            },
        ),
    ]
