# Generated by Django 4.1.2 on 2022-11-01 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0011_alter_dispute_claimer_alter_dispute_respondent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispute',
            name='closed_at',
            field=models.DateTimeField(null=True),
        ),
    ]