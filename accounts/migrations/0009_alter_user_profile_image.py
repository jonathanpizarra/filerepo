# Generated by Django 4.0.1 on 2022-01-24 05:33

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_remove_user_picture_path_alter_user_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(blank=True, default='profile_images/default_profile_img.jpg', null=True, upload_to=accounts.models.path_and_rename),
        ),
    ]
