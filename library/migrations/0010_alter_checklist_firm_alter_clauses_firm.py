# Generated by Django 4.1.3 on 2022-12-15 22:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0009_checklist_type_clauses_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checklist',
            name='firm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='library.firm'),
        ),
        migrations.AlterField(
            model_name='clauses',
            name='firm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='library.firm'),
        ),
    ]
