# Generated by Django 4.1.3 on 2023-04-07 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0062_emailtemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplate',
            name='actor_type',
            field=models.CharField(choices=[('respondent', 'respondent'), ('claimer', 'claimer')], default='claimer', max_length=24),
            preserve_default=False,
        ),
    ]
