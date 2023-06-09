# Generated by Django 4.1.5 on 2023-03-07 21:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0055_dispute_straight_to_hearing'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionNames',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_name', models.CharField(choices=[('Approve', 'Approve')], max_length=24)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Actions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(choices=[('Accept', 'Accept'), ('Reject', 'Reject'), ('Pending', 'Pending')], max_length=24)),
                ('action', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_values', to='litigation.actionnames')),
            ],
        ),
        migrations.RemoveField(
            model_name='dispute',
            name='straight_to_hearing',
        ),
        migrations.CreateModel(
            name='DisputeActorActions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('action', models.ManyToManyField(to='litigation.actions')),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='litigation.actor')),
                ('dispute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='litigation.dispute')),
            ],
        ),
    ]
