from django.db import models

# Create your models here.
"""
LOG EVENT TYPES :
Login
Logout
Registration
Profile update
Account deletion
File upload
File edit
File delete
File download
File restore
File view
Category creation
Category edit
Category delete
Catetory restore
Restore user
... pa-add kung may kulang
"""

class Log(models.Model):
    log_time = models.DateTimeField(auto_now_add=True)
    log_code = models.CharField(max_length=50)
    log_message = models.TextField()








