# Generated by Django 3.0.3 on 2020-04-10 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0004_auto_20200409_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='uses',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
