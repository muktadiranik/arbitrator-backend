# Generated by Django 4.1.3 on 2023-05-18 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='opening',
            name='linked_in_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
