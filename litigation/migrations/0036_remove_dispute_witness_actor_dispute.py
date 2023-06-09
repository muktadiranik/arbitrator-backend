# Generated by Django 4.1.3 on 2022-11-28 13:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0035_alter_claim_dispute'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dispute',
            name='witness',
        ),
        migrations.AddField(
            model_name='actor',
            name='dispute',
            field=models.ForeignKey(default=59, on_delete=django.db.models.deletion.CASCADE, related_name='witnesses', to='litigation.dispute'),
            preserve_default=False,
        ),
    ]
