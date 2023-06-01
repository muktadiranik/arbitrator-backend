# Generated by Django 4.1.3 on 2022-11-17 00:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0021_alter_offer_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evidence',
            name='attachment',
            field=models.FileField(upload_to='evidences/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'png', 'mp4'])]),
        ),
    ]
