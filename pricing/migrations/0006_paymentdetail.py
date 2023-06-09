# Generated by Django 4.1.3 on 2023-05-30 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0076_alter_settlementagreements_content'),
        ('pricing', '0005_rename_plans_plan'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('stripe_payment_status', models.CharField(choices=[('requires_payment_method', 'requires_payment_method'), ('requires_confirmation', 'requires_confirmation'), ('requires_action', 'requires_action'), ('processing', 'processing'), ('requires_capture', 'requires_capture'), ('succeeded', 'succeeded'), ('canceled', 'canceled'), ('failed', 'failed'), ('expired', 'expired'), ('void', 'void')], default='None', max_length=24)),
                ('stripe_payment_id', models.CharField(default='None', max_length=48)),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_details', to='litigation.actor')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
