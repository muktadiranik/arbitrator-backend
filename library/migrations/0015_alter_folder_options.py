# Generated by Django 4.1.3 on 2022-12-16 12:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0014_folder'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='folder',
            options={'ordering': ('sequence',)},
        ),
    ]
