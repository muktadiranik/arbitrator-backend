# Generated by Django 4.1.3 on 2022-11-12 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0017_alter_dispute_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='dispute',
            name='claimer_invitation_status',
            field=models.CharField(choices=[('sent', 'sent'), ('draft', 'draft'), ('pending', 'pending'), ('signed-up', 'signed-up')], default='pending', max_length=16),
        ),
        migrations.AddField(
            model_name='dispute',
            name='respondent_invitation_status',
            field=models.CharField(choices=[('sent', 'sent'), ('draft', 'draft'), ('pending', 'pending'), ('signed-up', 'signed-up')], default='pending', max_length=16),
        ),
    ]
