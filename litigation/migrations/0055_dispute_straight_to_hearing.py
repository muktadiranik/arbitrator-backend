# Generated by Django 4.1.5 on 2023-03-06 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0054_merge_20230306_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='dispute',
            name='straight_to_hearing',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]