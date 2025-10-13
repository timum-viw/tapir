import logging
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

log = logging.getLogger(__name__)


class APIKeyAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware that authenticates requests using an API key in the Authorization header.
    
    The API key should be provided in the Authorization header in the format:
    Authorization: Api-Key <your-api-key>
    
    If a valid API key is provided, the request.user will be set to the user
    associated with that API key.
    """

    def process_request(self, request):
        # Skip if user is already authenticated via session
        if hasattr(request, 'user') and request.user.is_authenticated:
            return

        # Check for API key in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Api-Key '):
            return
        
        # Extract the API key
        api_key = auth_header[8:].strip()  # Remove 'Api-Key ' prefix
        
        if not api_key:
            return
        
        # Import here to avoid circular imports
        from tapir.accounts.api_key_models import APIKey
        
        try:
            # Find the API key and authenticate the user
            api_key_obj = APIKey.objects.select_related('user').get(
                key=api_key,
                is_active=True
            )
            
            # Set the user on the request
            request.user = api_key_obj.user
            
            # Update last_used_at timestamp
            api_key_obj.last_used_at = timezone.now()
            api_key_obj.save(update_fields=['last_used_at'])
            
            log.debug(f"Authenticated user {request.user.username} via API key {api_key_obj.name}")
            
        except APIKey.DoesNotExist:
            log.warning(f"Invalid API key attempt: {api_key[:8]}...")
            # Don't authenticate - leave request.user as AnonymousUser
            pass
        except Exception as e:
            log.error(f"Error during API key authentication: {e}")
            pass

