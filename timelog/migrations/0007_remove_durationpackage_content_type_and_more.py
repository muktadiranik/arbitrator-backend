# Generated by Django 4.1.3 on 2023-02-09 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timelog', '0006_durationpackage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='durationpackage',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='durationpackage',
            name='object_id',
        ),
    ]
