# Generated by Django 3.0.5 on 2020-04-18 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0008_auto_20200418_1855'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='excluded_dates',
            field=models.ManyToManyField(blank=True, related_name='excluded', to='cal.ExcludedDates'),
        ),
    ]
