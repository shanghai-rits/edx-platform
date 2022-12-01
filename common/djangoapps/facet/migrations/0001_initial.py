# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Facet',
            fields=[
                ('displayname', models.CharField(unique=True, max_length=100)),
                ('number', models.AutoField(serialize=False, primary_key=True)),
                ('comment', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'facet',
            },
        ),
        migrations.CreateModel(
            name='FacetOfCourse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('facet', models.CharField(max_length=100)),
                ('group', models.CharField(max_length=100)),
                ('course', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'facet_group_course',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('facet', models.CharField(max_length=100)),
                ('group', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'facet_group',
            },
        ),
    ]
