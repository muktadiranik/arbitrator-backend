# Generated by Django 4.1.3 on 2022-11-23 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0029_alter_actor_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actor',
            name='type',
            field=models.SlugField(blank=True, choices=[('arbitrator', 'Arbitrator'), ('claimer', 'Claimer'), ('creator', 'Creator'), ('witness', 'Witness'), ('respondent', 'Respondent')], max_length=25, null=True),
        ),
    ]
