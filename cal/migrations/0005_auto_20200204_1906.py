# Generated by Django 3.0.3 on 2020-02-05 02:06

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0004_auto_20200204_1902'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='description',
            field=models.CharField(default='', max_length=500, verbose_name='Describe the event briefly. What type of work will be done?'),
        ),
        migrations.AddField(
            model_name='event',
            name='title',
            field=models.CharField(default='', max_length=75, verbose_name='What is the name of the event?'),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_repeat',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 4, 2, 6, 40, 779467, tzinfo=utc), verbose_name='end repeat date'),
        ),
    ]