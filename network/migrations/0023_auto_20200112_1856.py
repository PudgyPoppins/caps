# Generated by Django 3.0.2 on 2020-01-13 01:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0022_auto_20200112_1852'),
    ]

    operations = [
        migrations.RenameField(
            model_name='network',
            old_name='netslug',
            new_name='slug',
        ),
        migrations.RenameField(
            model_name='nonprofit',
            old_name='nonslug',
            new_name='slug',
        ),
    ]
