# Generated by Django 4.1.3 on 2022-12-20 11:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0041_merge_20221206_0955'),
        ('library', '0020_alter_folder_case_alter_folder_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='case',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='folders', to='litigation.dispute'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='folders', to='library.folder'),
        ),
    ]
