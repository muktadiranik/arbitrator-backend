# Generated by Django 4.1.5 on 2023-01-30 10:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SectionTitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=24)),
            ],
        ),
        migrations.CreateModel(
            name='TermSheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(max_length=24)),
            ],
        ),
        migrations.CreateModel(
            name='TermsheetTitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=24)),
            ],
        ),
        migrations.CreateModel(
            name='TermsheetSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=24)),
                ('text', models.TextField()),
                ('termsheet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='termsheet.termsheet')),
            ],
        ),
        migrations.CreateModel(
            name='DigitalSignature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=18)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('termsheet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signatures', to='termsheet.termsheet')),
            ],
        ),
    ]