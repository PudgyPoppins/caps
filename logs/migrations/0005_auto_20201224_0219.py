# Generated by Django 3.1.4 on 2020-12-24 02:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0028_auto_20201222_0437'),
        ('logs', '0004_log_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='attendee',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log', to='cal.attendee'),
        ),
    ]
