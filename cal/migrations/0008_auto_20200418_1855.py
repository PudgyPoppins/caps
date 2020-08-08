# Generated by Django 3.0.5 on 2020-04-18 18:55

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0007_auto_20200328_1501'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcludedDates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='excluded date')),
            ],
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['-start_time']},
        ),
        migrations.AlterField(
            model_name='calendar',
            name='custom_calendar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usercal', to='cal.Calendar'),
        ),
        migrations.AlterField(
            model_name='calendar',
            name='excluded_calendars',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='excludedcal', to='cal.Calendar'),
        ),
        migrations.AlterField(
            model_name='event',
            name='recurrence',
            field=models.CharField(blank=True, help_text='Will this event ever repeat?', max_length=1000, null=True),
        ),
    ]