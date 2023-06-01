# Generated by Django 4.1.2 on 2022-10-28 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0002_alter_uuid_expires_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uuid',
            name='expires_at',
        ),
        migrations.AddField(
            model_name='uuid',
            name='max_age',
            field=models.PositiveIntegerField(default=172800),
        ),
    ]