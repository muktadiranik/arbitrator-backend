# Generated by Django 4.1.3 on 2022-11-16 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0018_dispute_claimer_invitation_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='first_address',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='dispute',
            name='status',
            field=models.CharField(choices=[('in-progress', 'in-progress'), ('resolved', 'resolved'), ('unresolved', 'unresolved'), ('waiting-for-sign-up', 'waiting-for-sign-up')], max_length=24),
        ),
    ]