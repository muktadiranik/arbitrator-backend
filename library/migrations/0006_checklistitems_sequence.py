# Generated by Django 4.1.3 on 2022-12-15 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_alter_checklist_sequence_alter_clauses_sequence'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklistitems',
            name='sequence',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]