# Generated by Django 4.1.3 on 2022-11-09 22:30

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0014_alter_address_second_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Timezone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offset', models.CharField(max_length=32)),
                ('description', models.CharField(max_length=128)),
                ('actor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='litigation.actor')),
            ],
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(max_length=10)),
                ('counter_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('counter_amount_currency', models.CharField(max_length=10)),
                ('status', models.CharField(choices=[('counter', 'counter'), ('rejected', 'rejected'), ('accepted', 'accepted')], max_length=16)),
                ('claim', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='litigation.claim')),
            ],
        ),
        migrations.CreateModel(
            name='Evidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment', models.FileField(upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'word', 'jpg', 'png', 'mp4'])])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('claim', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='litigation.claim')),
            ],
        ),
    ]
