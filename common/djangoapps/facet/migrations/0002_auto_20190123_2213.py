# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facet', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupOfLanguage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lang', models.CharField(max_length=100)),
                ('content', models.CharField(max_length=100)),
                ('group', models.ForeignKey(related_name='group_lang', to='facet.Group', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'db_table': 'facet_group_lang',
            },
        ),
        migrations.AlterUniqueTogether(
            name='groupoflanguage',
            unique_together=set([('lang', 'group')]),
        ),
    ]
