# Generated by Django 1.11.27 on 2020-01-13 13:55


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0017_auto_20191002_0823'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='courseoverview',
            name='start_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='historicalcourseoverview',
            name='end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='historicalcourseoverview',
            name='start_date',
            field=models.DateTimeField(null=True),
        ),
    ]
