# Generated by Django 4.0.1 on 2022-01-23 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fileupload',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
    ]
