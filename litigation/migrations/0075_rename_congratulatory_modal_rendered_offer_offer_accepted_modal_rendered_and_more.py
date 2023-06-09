# Generated by Django 4.1.3 on 2023-05-05 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0074_offer_congratulatory_modal_rendered'),
    ]

    operations = [
        migrations.RenameField(
            model_name='offer',
            old_name='congratulatory_modal_rendered',
            new_name='offer_accepted_modal_rendered',
        ),
        migrations.AddField(
            model_name='offer',
            name='offer_received_modal_rendered',
            field=models.BooleanField(default=False),
        ),
    ]
