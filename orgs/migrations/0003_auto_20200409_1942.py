# Generated by Django 3.0.3 on 2020-04-10 01:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orgs', '0002_auto_20200328_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='leader',
            field=models.ManyToManyField(blank=True, related_name='leaders', related_query_name='leader', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='organization',
            name='member',
            field=models.ManyToManyField(blank=True, related_name='members', related_query_name='member', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='organization',
            name='moderator',
            field=models.ManyToManyField(blank=True, related_name='moderators', related_query_name='moderator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='organization',
            name='public',
            field=models.BooleanField(default=True, help_text='whether or not members can join without an invitation / approval'),
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expiration', models.DateTimeField(blank=True, help_text='after this date, this link will no longer be valid', null=True)),
                ('valid', models.BooleanField(default=True)),
                ('token', models.CharField(max_length=5)),
                ('organization', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='orgs.Organization')),
                ('user', models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
