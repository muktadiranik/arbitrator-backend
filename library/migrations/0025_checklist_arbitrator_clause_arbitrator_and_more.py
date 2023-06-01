# Generated by Django 4.1.3 on 2022-12-29 19:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0042_dispute_arbitrator'),
        ('library', '0024_alter_checklistitem_checklist'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklist',
            name='arbitrator',
            field=models.ForeignKey(default=404, on_delete=django.db.models.deletion.PROTECT, related_name='checklists', to='litigation.arbitrator'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clause',
            name='arbitrator',
            field=models.ForeignKey(default=404, on_delete=django.db.models.deletion.PROTECT, related_name='clauses', to='litigation.arbitrator'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='folder',
            name='arbitrator',
            field=models.ForeignKey(default=404, on_delete=django.db.models.deletion.PROTECT, related_name='folders', to='litigation.arbitrator'),
            preserve_default=False,
        ),
    ]