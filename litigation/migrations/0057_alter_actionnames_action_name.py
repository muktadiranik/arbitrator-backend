# Generated by Django 4.1.5 on 2023-03-07 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0056_actionnames_actions_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionnames',
            name='action_name',
            field=models.CharField(choices=[('Approve', 'Approve'), ('Straight to hearing', 'Straight to hearing')], max_length=24),
        ),
    ]