"""
Django REST Framework authentication class for API keys.
"""
from rest_framework import authentication
from rest_framework import exceptions
from tapir.accounts.api_key_models import APIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    API Key authentication for Django REST Framework.
    
    Clients should authenticate by passing the API key in the "Authorization"
    HTTP header, prepended with the string "Api-Key ".  For example:
    
        Authorization: Api-Key 401f7ac837da42b97f613d789819ff93537bee6a
    """
    
    keyword = 'Api-Key'

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid API key header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid API key header. API key string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            api_key = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid API key header. API key string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(api_key)

    def authenticate_credentials(self, key):
        try:
            api_key = APIKey.objects.select_related('user').get(key=key, is_active=True)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key.')

        if not api_key.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        # Update last_used_at
        from django.utils import timezone
        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=['last_used_at'])

        return (api_key.user, api_key)

    def authenticate_header(self, request):
        return self.keyword

