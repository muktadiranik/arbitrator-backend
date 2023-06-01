# Generated by Django 4.1.2 on 2022-10-27 14:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(blank=True, choices=[('individual', 'individual'), ('organization', 'organization')], max_length=16, null=True)),
                ('type', models.SlugField(blank=True, choices=[('arbitrator', 'Arbitrator'), ('claimer', 'Claimer'), ('creator', 'Creator'), ('witness', 'Witness'), ('respondent', 'Respondent')], max_length=25, null=True)),
                ('category', models.CharField(blank=True, choices=[('general_contractor', 'General Contractor')], max_length=32, null=True)),
                ('company', models.CharField(blank=True, max_length=32, null=True)),
                ('phone_number', models.CharField(max_length=16, verbose_name='Phone Number')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('signed_up_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UUID',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='litigation.actor')),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_address', models.CharField(max_length=128)),
                ('second_address', models.CharField(max_length=128)),
                ('city', models.CharField(blank=True, max_length=32, null=True)),
                ('state', models.CharField(blank=True, choices=[('California', 'California')], max_length=32, null=True)),
                ('zip', models.CharField(blank=True, max_length=16, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='litigation.actor')),
            ],
        ),
        migrations.CreateModel(
            name='Arbitrator',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('litigation.actor',),
        ),
        migrations.CreateModel(
            name='Claimer',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('litigation.actor',),
        ),
        migrations.CreateModel(
            name='Creator',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('litigation.actor',),
        ),
        migrations.CreateModel(
            name='Respondent',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('litigation.actor',),
        ),
        migrations.CreateModel(
            name='Witness',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('litigation.actor',),
        ),
    ]