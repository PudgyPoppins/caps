# Generated by Django 3.0.2 on 2020-02-02 21:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField(default=django.utils.timezone.now, verbose_name='starting time')),
                ('end_time', models.TimeField(default=django.utils.timezone.now, verbose_name='ending time')),
                ('all_day', models.BooleanField(default=False, verbose_name='will this event last the entire day')),
            ],
        ),
    ]
