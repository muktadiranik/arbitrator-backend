# Generated by Django 4.1.3 on 2022-11-23 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0030_alter_actor_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
