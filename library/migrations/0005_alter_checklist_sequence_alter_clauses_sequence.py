# Generated by Django 4.1.3 on 2022-12-15 14:15

from django.db import migrations, models
import library.models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0004_checklist_firm_checklist_isglobal_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checklist',
            name='sequence',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='clauses',
            name='sequence',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
