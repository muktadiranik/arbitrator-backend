# Generated by Django 4.1.5 on 2023-01-30 10:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0043_alter_address_user_alter_evidence_claim_and_more'),
        ('termsheet', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='termsheet',
            name='dispute',
            field=models.ForeignKey(default=66, on_delete=django.db.models.deletion.CASCADE, to='litigation.dispute'),
            preserve_default=False,
        ),
    ]
