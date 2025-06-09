from django.contrib import admin
from .models import UserCloudProvider, FileSyncStatus
@admin.register(UserCloudProvider)
class UserCloudProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider_name', 'created_at', 'updated_at')
    search_fields = ('user__username', 'provider_name')
    list_filter = ('provider_name',)
    ordering = ('-created_at',)
@admin.register(FileSyncStatus)
class FileSyncStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'file_name', 'sync_status', 'last_synced_at')
    search_fields = ('user__username', 'file_name')
    list_filter = ('sync_status', 'provider__provider_name')
    ordering = ('-last_synced_at',)