# Generated by Django 3.0.8 on 2020-11-12 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0013_auto_20201112_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='expiration',
            field=models.DurationField(blank=True, help_text='after this time, this link will no longer be valid', null=True),
        ),
    ]
