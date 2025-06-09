from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.


class UserCloudProvider(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider_name = models.CharField(max_length=20, choices=settings.CLOUD_PROVIDERS)
    email = models.EmailField(max_length=255, blank=True, null=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    extra_data = models.JSONField(blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'provider_name', 'email')

    def __str__(self):
        return f"{self.user.username} - {self.provider_name}"

class FileSyncStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(UserCloudProvider, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    sync_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    last_synced_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file_name} - {self.sync_status} ({self.user.username})"
    
    