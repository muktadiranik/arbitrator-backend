# Generated by Django 4.1.3 on 2023-05-04 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0072_alter_settlementagreements_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settlementagreements',
            name='content',
            field=models.TextField(max_length=40000),
        ),
    ]