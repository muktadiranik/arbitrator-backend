# Generated by Django 4.1.3 on 2022-11-11 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0016_rename_id_claim_dispute_offer_creator_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispute',
            name='status',
            field=models.CharField(choices=[('in-progress', 'in-progress'), ('resolved', 'resolved'), ('unresolved', 'unresolved'), ('Waiting-for-sign-up', 'waiting-for-sign-up')], max_length=24),
        ),
    ]
