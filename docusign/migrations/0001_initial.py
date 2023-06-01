# Generated by Django 4.1.3 on 2023-04-18 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('litigation', '0068_alter_evidence_attachment'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocuSignEnvelope',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('envelope_id', models.CharField(max_length=96)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('signed_up_at', models.DateTimeField(auto_now_add=True)),
                ('dispute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='envelope', to='litigation.dispute')),
            ],
        ),
    ]