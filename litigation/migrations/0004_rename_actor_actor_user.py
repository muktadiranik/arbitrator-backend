# Generated by Django 4.1.2 on 2022-10-28 11:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0003_remove_uuid_expires_at_uuid_max_age'),
    ]

    operations = [
        migrations.RenameField(
            model_name='actor',
            old_name='actor',
            new_name='user',
        ),
    ]