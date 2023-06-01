# Generated by Django 4.1.2 on 2022-11-01 20:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0010_alter_dispute_claimer_alter_dispute_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispute',
            name='claimer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='disputes_claimed', to='litigation.claimer'),
        ),
        migrations.AlterField(
            model_name='dispute',
            name='respondent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='disputes', to='litigation.respondent'),
        ),
    ]