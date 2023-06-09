# Generated by Django 4.1.3 on 2022-11-11 12:33

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('litigation', '0015_timezone_offer_evidence'),
    ]

    operations = [
        migrations.RenameField(
            model_name='claim',
            old_name='id',
            new_name='dispute',
        ),
        migrations.AddField(
            model_name='offer',
            name='creator',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='litigation.actor'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dispute',
            name='status',
            field=models.CharField(choices=[('in-progress', 'in-progress'), ('answered', 'answered'), ('unanswered', 'unanswered'), ('pending-signup', 'pending-signup')], max_length=16),
        ),
        migrations.AlterField(
            model_name='evidence',
            name='attachment',
            field=models.FileField(upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'png', 'mp4'])]),
        ),
        migrations.AlterField(
            model_name='offer',
            name='currency',
            field=models.CharField(default='usd', max_length=10),
        ),
        migrations.AlterField(
            model_name='offer',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('counter', 'counter'), ('rejected', 'rejected'), ('accepted', 'accepted')], max_length=16),
        ),
    ]
