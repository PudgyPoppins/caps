# Generated by Django 3.0 on 2019-12-30 23:25

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0011_auto_20191230_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nonprofit',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 12, 30, 23, 25, 25, 523457, tzinfo=utc), verbose_name='date published'),
        ),
    ]
