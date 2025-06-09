from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from .models import UserCloudProvider
from google_auth_oauthlib.flow import Flow
from django.shortcuts import redirect
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


# Create your views here.


@login_required
def dashboard(request):
    connected_providers = UserCloudProvider.objects.filter(user=request.user).order_by('-created_at')
    
    # Add a method to check if token is valid (you can customize this logic)
    for provider in connected_providers:
        provider.is_token_valid = provider.token_expiry is None or provider.token_expiry > timezone.now()
    
    # Get recent sync activity
    from .models import FileSyncStatus
    recent_syncs = FileSyncStatus.objects.filter(
        user=request.user
    ).select_related('provider').order_by('-last_synced_at')[:10]
    
    # Calculate total files (you can customize this based on your needs)
    total_files = FileSyncStatus.objects.filter(user=request.user).count()
    
    context = {
        'connected_providers': connected_providers,
        'recent_syncs': recent_syncs,
        'total_files': total_files,
    }
    
    return render(request, 'cloud_provider/dashboard.html', context)

    

@login_required
def connect_provider(request):
    # Get already connected providers
    connected_providers = UserCloudProvider.objects.filter(user=request.user).order_by('-created_at')
    
    # Add a method to check if token is valid
    for provider in connected_providers:
        provider.is_token_valid = provider.token_expiry is None or provider.token_expiry > timezone.now()
    
    context = {
        'connected_providers': connected_providers,
    }
    
    return render(request, 'cloud_provider/connect_provider.html', context)


@login_required
def connect_google_drive(request):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes = [
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ]
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='false',
        prompt='consent'
    )
    request.session['google_oauth_state'] = state
    return redirect(authorization_url)

@login_required
def google_drive_callback(request):
    state = request.session.get('google_oauth_state')
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes = [
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ],
        state=state
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    print(credentials)

    id_info = id_token.verify_oauth2_token(
        credentials.id_token,
        google_requests.Request(),
        settings.GOOGLE_CLIENT_ID
    )

    email = id_info.get("email")
    email_verified = id_info.get("email_verified")
    sub = id_info.get("sub")  # Unique Google user ID
 
    user_cloud_provider, created = UserCloudProvider.objects.get_or_create(
    user=request.user,
    provider_name='google_drive',
    email=email,
    defaults={
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_expiry': credentials.expiry,
            'extra_data': {
                'id_token': credentials.id_token,
                'scope': credentials.scopes,
                'email_verified': email_verified,
                'sub': sub
            }
        }
    )

    if not created:
        user_cloud_provider.access_token = credentials.token
        user_cloud_provider.refresh_token = credentials.refresh_token
        user_cloud_provider.token_expiry = credentials.expiry
        user_cloud_provider.extra_data = {
            'id_token': credentials.id_token,
            'scope': credentials.scopes,
            'email_verified': email_verified,
            'sub': sub
        }
        user_cloud_provider.save()

    messages.success(request, 'Google Drive connected successfully!')
    return redirect('cloud_provider:dashboard')


@login_required
def disconnect_provider(request, provider_id):
    """Disconnect a cloud provider"""
    if request.method == 'POST':
        try:
            provider = UserCloudProvider.objects.get(
                id=provider_id,
                user=request.user
            )
            # Get readable provider name
            provider_name = 'Google Drive' if provider.provider_name == 'google_drive' else 'OneDrive'
            provider.delete()
            messages.success(request, f'{provider_name} account has been disconnected successfully.')
        except UserCloudProvider.DoesNotExist:
            messages.error(request, 'Provider not found or you do not have permission to disconnect it.')
    
    return redirect('cloud_provider:dashboard')


@login_required
def connect_onedrive(request):
    """Placeholder for OneDrive connection - to be implemented"""
    messages.info(request, 'OneDrive integration is coming soon!')
    return redirect('cloud_provider:connect_provider')


@login_required
def onedrive_callback(request):
    """Placeholder for OneDrive callback - to be implemented"""
    messages.info(request, 'OneDrive integration is coming soon!')
    return redirect('cloud_provider:connect_provider')