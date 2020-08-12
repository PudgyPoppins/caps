# Generated by Django 3.0.8 on 2020-08-12 03:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0023_auto_20200812_0251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.TimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='ending time'),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_time',
            field=models.TimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='starting time'),
        ),
    ]