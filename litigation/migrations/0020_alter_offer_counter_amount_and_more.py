# Generated by Django 4.1.3 on 2022-11-16 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0019_alter_address_first_address_alter_dispute_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='counter_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='counter_amount_currency',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
