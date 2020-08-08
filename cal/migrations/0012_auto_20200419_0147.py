# Generated by Django 3.0.5 on 2020-04-19 01:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cal', '0011_auto_20200419_0137'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='event',
            name='nonprofit_reps',
            field=models.ManyToManyField(blank=True, related_name='nonprofit_rep', to=settings.AUTH_USER_MODEL),
        ),
    ]