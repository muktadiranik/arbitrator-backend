# Generated by Django 4.1.3 on 2022-12-15 22:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_firm_remove_checklist_isglobal_and_more'),
    ]

    operations = [
        migrations.AlterOrderWithRespectTo(
            name='checklist',
            order_with_respect_to='sequence',
        ),
        migrations.AlterOrderWithRespectTo(
            name='checklistitems',
            order_with_respect_to='sequence',
        ),
        migrations.AlterOrderWithRespectTo(
            name='clauses',
            order_with_respect_to='sequence',
        ),
    ]
