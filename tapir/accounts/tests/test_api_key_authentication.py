from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from tapir.accounts.models import TapirUser
from tapir.accounts.api_key_models import APIKey
from tapir.accounts.api_key_middleware import APIKeyAuthenticationMiddleware


class APIKeyAuthenticationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = APIKeyAuthenticationMiddleware(get_response=lambda r: None)
        
        # Create a test user
        self.user = TapirUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        # Create an API key for the user
        self.api_key = APIKey.objects.create(
            user=self.user,
            name="Test API Key"
        )
        
    def test_api_key_generation(self):
        """Test that API keys are generated automatically"""
        self.assertIsNotNone(self.api_key.key)
        self.assertEqual(len(self.api_key.key), 64)
        
    def test_valid_api_key_authentication(self):
        """Test authentication with a valid API key"""
        request = self.factory.get('/api/test/')
        request.user = AnonymousUser()
        request.META['HTTP_AUTHORIZATION'] = f'Api-Key {self.api_key.key}'
        
        self.middleware.process_request(request)
        
        self.assertTrue(request.user.is_authenticated)
        self.assertEqual(request.user, self.user)
        
    def test_invalid_api_key(self):
        """Test that invalid API keys don't authenticate"""
        request = self.factory.get('/api/test/')
        request.user = AnonymousUser()
        request.META['HTTP_AUTHORIZATION'] = 'Api-Key invalid-key-12345'
        
        self.middleware.process_request(request)
        
        self.assertFalse(request.user.is_authenticated)
        
    def test_inactive_api_key(self):
        """Test that inactive API keys don't authenticate"""
        self.api_key.is_active = False
        self.api_key.save()
        
        request = self.factory.get('/api/test/')
        request.user = AnonymousUser()
        request.META['HTTP_AUTHORIZATION'] = f'Api-Key {self.api_key.key}'
        
        self.middleware.process_request(request)
        
        self.assertFalse(request.user.is_authenticated)
        
    def test_malformed_authorization_header(self):
        """Test that malformed headers don't cause errors"""
        request = self.factory.get('/api/test/')
        request.user = AnonymousUser()
        request.META['HTTP_AUTHORIZATION'] = 'Bearer sometoken'
        
        self.middleware.process_request(request)
        
        self.assertFalse(request.user.is_authenticated)
        
    def test_no_authorization_header(self):
        """Test that requests without Authorization header don't cause errors"""
        request = self.factory.get('/api/test/')
        request.user = AnonymousUser()
        
        self.middleware.process_request(request)
        
        self.assertFalse(request.user.is_authenticated)
        
    def test_already_authenticated_user_not_overridden(self):
        """Test that already authenticated users are not overridden"""
        other_user = TapirUser.objects.create_user(
            username="otheruser",
            email="other@example.com"
        )
        
        request = self.factory.get('/api/test/')
        request.user = other_user
        request.META['HTTP_AUTHORIZATION'] = f'Api-Key {self.api_key.key}'
        
        self.middleware.process_request(request)
        
        # User should remain the same (not overridden by API key)
        self.assertEqual(request.user, other_user)
        
    def test_last_used_at_updated(self):
        """Test that last_used_at timestamp is updated on use"""
        initial_last_used = self.api_key.last_used_at
        
        request = self.factory.get('/api/test/')
        request.user = AnonymousUser()
        request.META['HTTP_AUTHORIZATION'] = f'Api-Key {self.api_key.key}'
        
        self.middleware.process_request(request)
        
        self.api_key.refresh_from_db()
        self.assertIsNotNone(self.api_key.last_used_at)
        if initial_last_used:
            self.assertGreater(self.api_key.last_used_at, initial_last_used)


class APIKeyModelTest(TestCase):
    def setUp(self):
        self.user = TapirUser.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
        
    def test_api_key_creation(self):
        """Test creating an API key"""
        api_key = APIKey.objects.create(
            user=self.user,
            name="Test Key"
        )
        
        self.assertIsNotNone(api_key.key)
        self.assertEqual(api_key.user, self.user)
        self.assertEqual(api_key.name, "Test Key")
        self.assertTrue(api_key.is_active)
        
    def test_api_key_matches(self):
        """Test the matches method"""
        api_key = APIKey.objects.create(
            user=self.user,
            name="Test Key"
        )
        
        self.assertTrue(api_key.matches(api_key.key))
        self.assertFalse(api_key.matches("wrong-key"))
        
    def test_api_key_str_representation(self):
        """Test the string representation"""
        api_key = APIKey.objects.create(
            user=self.user,
            name="Test Key"
        )
        
        str_repr = str(api_key)
        self.assertIn("Test Key", str_repr)
        self.assertIn(self.user.username, str_repr)
        self.assertIn(api_key.key[:8], str_repr)

