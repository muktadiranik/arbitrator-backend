# Generated by Django 4.1.3 on 2023-04-07 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0065_remove_emailtemplate_dispute_code_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailtemplate',
            name='actor_type',
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='actor',
            field=models.ForeignKey(default=560, on_delete=django.db.models.deletion.CASCADE, to='litigation.actor'),
            preserve_default=False,
        ),
    ]