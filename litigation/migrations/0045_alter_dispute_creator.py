# Generated by Django 4.1.5 on 2023-02-24 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0044_alter_claim_claimed_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispute',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disputes_created', to='litigation.creator'),
        ),
    ]
