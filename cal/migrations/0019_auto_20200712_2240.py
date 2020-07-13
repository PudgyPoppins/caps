# Generated by Django 3.0.5 on 2020-07-12 22:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cal', '0018_remove_event_total_attending'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='attendees',
        ),
        migrations.AddField(
            model_name='attendee',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attendee', to='cal.Event'),
        ),
        migrations.AlterField(
            model_name='attendee',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
