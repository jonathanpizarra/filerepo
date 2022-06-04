from django.db import models
from accounts.models import User
import os
# Create your models here.

PATH = 'files/' # make sure to have 1 forward slash only (no subfolders) to avoid conflicts on getting filename on other parts of the code

class Category(models.Model):
    
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, default="")
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edit_date = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    creator = models.ForeignKey(User, related_name="category_creator", on_delete=models.CASCADE)
    last_editor = models.ForeignKey(User, related_name="category_last_editor", on_delete=models.CASCADE)

    
    
    def __str__(self):
            return self.name

class FileUpload(models.Model):
    
    upload_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    last_editor = models.ForeignKey(User, related_name="fileupload_last_editor", on_delete=models.CASCADE)
    last_edit_date = models.DateTimeField(auto_now=True)
    uploaded_file = models.FileField(upload_to=PATH, null=True, blank=True)
    uploader = models.ForeignKey(User, related_name="fileupload_uploader", on_delete=models.CASCADE)
    is_archived = models.BooleanField(default=False)
    description = models.CharField(max_length=200, default="")

    def get_filename(self):
        return self.uploaded_file.name[len(PATH):]

    def __str__(self):
        return self.uploaded_file.name[len(PATH):]

    def rename(self, new_name):
        old_path = self.uploaded_file.path
        self.uploaded_file.name = PATH + new_name

        os.rename(old_path, self.uploaded_file.path)
        self.save()


    




