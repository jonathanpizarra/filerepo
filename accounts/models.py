from django.db import models
from uuid import uuid4
import os
# Create your models here.

#
# django-admin superuser account : 
# #
# username: admin
# password: django1234
# 

def path_and_rename(instance, filename):
    ext = filename.split('.')[-1]
    upload_to = 'profile_images/'
    filename = '{}.{}'.format(uuid4().hex, ext)
    return os.path.join(upload_to, filename)

class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True, blank=False)
    password = models.CharField(max_length=100, blank=False)
    email = models.EmailField(max_length=100, blank=False)
    is_archived = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to=path_and_rename, default='profile_images/default_profile_img.png', null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username




    