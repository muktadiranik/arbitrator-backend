# Generated by Django 4.1.3 on 2023-05-04 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0070_remove_settlementagreements_template_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settlementagreements',
            name='content',
            field=models.TextField(max_length=5000),
        ),
    ]
