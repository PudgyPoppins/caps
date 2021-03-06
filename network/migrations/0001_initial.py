# Generated by Django 3.0.2 on 2020-01-29 03:04

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date published')),
                ('title', models.CharField(default='', help_text='What town/city/location will this network be representing?', max_length=75, unique=True)),
                ('src_link', models.URLField(blank=True, help_text='Enter a url for an image representing the network location')),
                ('src_file', models.ImageField(blank=True, help_text='Submit a file for an image representing the network location', upload_to='network_images')),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('lat', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('lon', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('flagged', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Nonprofit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date published')),
                ('title', models.CharField(help_text='Enter the network name', max_length=75)),
                ('src_link', models.URLField(blank=True, help_text='Enter a url for an image representing the network location')),
                ('src_file', models.ImageField(blank=True, help_text='Submit a file for an image representing the network location', upload_to='nonprofit_images')),
                ('website', models.URLField(blank=True, help_text='Enter the nonprofit website url, if applicable', null=True)),
                ('phone', models.CharField(blank=True, help_text='Enter a phone number in the format 111-111-1111', max_length=12, null=True)),
                ('address', models.CharField(blank=True, help_text='Enter the nonprofit address, if applicable', max_length=100, null=True)),
                ('email', models.EmailField(blank=True, help_text='Please enter a relevant email for volunteering, if applicable', max_length=254, null=True)),
                ('description', models.CharField(blank=True, help_text='What kind of work will volunteers be doing here?', max_length=1024, null=True)),
                ('lat', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('lon', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('flagged', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True, max_length=100)),
                ('network', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.Network')),
                ('tags', models.ManyToManyField(blank=True, to='network.Tag')),
            ],
        ),
        migrations.AddConstraint(
            model_name='nonprofit',
            constraint=models.UniqueConstraint(fields=('network', 'title'), name='unique_np_naming'),
        ),
    ]
