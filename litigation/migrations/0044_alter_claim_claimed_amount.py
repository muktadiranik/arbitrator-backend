# Generated by Django 4.1.3 on 2023-02-09 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0043_alter_address_user_alter_evidence_claim_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='claimed_amount',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
    ]
