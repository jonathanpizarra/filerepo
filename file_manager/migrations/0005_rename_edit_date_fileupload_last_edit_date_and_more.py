# Generated by Django 4.0.1 on 2022-01-24 15:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('file_manager', '0004_alter_fileupload_uploader'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fileupload',
            old_name='edit_date',
            new_name='last_edit_date',
        ),
        migrations.AddField(
            model_name='category',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='last_edit_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
