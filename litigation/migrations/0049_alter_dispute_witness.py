# Generated by Django 4.1.5 on 2023-02-27 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0048_alter_dispute_witness'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispute',
            name='witness',
            field=models.ManyToManyField(blank=True, related_name='disputes_witnessed', to='litigation.witness'),
        ),
    ]
