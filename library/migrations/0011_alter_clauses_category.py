# Generated by Django 4.1.3 on 2022-12-15 22:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0010_alter_checklist_firm_alter_clauses_firm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clauses',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='library.category'),
        ),
    ]
