# Generated by Django 4.1.3 on 2023-01-29 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timelog', '0004_alter_timelog_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='timelog',
            name='stopped',
            field=models.BooleanField(default=False),
        ),
    ]
