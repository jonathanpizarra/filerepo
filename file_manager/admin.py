from django.contrib import admin
from .models import Category, FileUpload
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'creation_date', 'last_edit_date', )

class FileUploadAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'upload_date', 'last_edit_date', )

admin.site.register(Category, CategoryAdmin)
admin.site.register(FileUpload, FileUploadAdmin)