from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ops_user = models.BooleanField(default=False)

class File(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.owner}"

class FilePermission(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    encrypted_url = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return self.user
