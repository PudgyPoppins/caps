# Generated by Django 3.0.3 on 2020-02-07 00:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0016_auto_20200205_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendar',
            name='network_calendar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cal.Calendar'),
        ),
    ]
