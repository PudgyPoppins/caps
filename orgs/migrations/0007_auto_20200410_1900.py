# Generated by Django 3.0.3 on 2020-04-10 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0006_auto_20200409_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='uses',
            field=models.IntegerField(default=0),
        ),
    ]