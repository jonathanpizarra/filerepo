# Generated by Django 4.0.1 on 2022-01-24 11:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_user_profile_image'),
        ('file_manager', '0003_remove_fileupload_uploader_id_fileupload_uploader'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='uploader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.user'),
        ),
    ]
