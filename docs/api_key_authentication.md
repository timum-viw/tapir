# API Key Authentication

This document describes how to use API key authentication in Tapir.

## Overview

The API key authentication system allows external services or applications to authenticate as a specific user by providing an API key in the Authorization header. This is useful for:

- Mobile applications
- External services/integrations
- Automated scripts
- Third-party applications

The system includes:
- Middleware for authenticating regular Django views
- Django REST Framework authentication class for API endpoints
- Admin interface for managing API keys
- Automatic tracking of last usage

## Creating an API Key

API keys can be created through the Django admin interface:

1. Log in to the Django admin panel
2. Navigate to "Accounts" → "API Keys"
3. Click "Add API Key"
4. Fill in the following fields:
   - **Name**: A descriptive name for the API key (e.g., "Mobile App", "External Integration")
   - **User**: Select the user this API key will authenticate as
   - **Is active**: Check this to enable the API key
5. Click "Save"
6. **Important**: Copy the generated API key immediately - you won't be able to see it again!

## Using an API Key

To authenticate using an API key, include it in the Authorization header of your HTTP requests:

```
Authorization: Api-Key <your-api-key-here>
```

### Example with curl

```bash
curl -H "Authorization: Api-Key your-api-key-here" \
     https://your-tapir-instance.com/api/endpoint
```

### Example with Python requests

```python
import requests

api_key = "your-api-key-here"
headers = {
    "Authorization": f"Api-Key {api_key}"
}

response = requests.get(
    "https://your-tapir-instance.com/api/endpoint",
    headers=headers
)
```

### Example with JavaScript/fetch

```javascript
const apiKey = "your-api-key-here";

fetch("https://your-tapir-instance.com/api/endpoint", {
  headers: {
    "Authorization": `Api-Key ${apiKey}`
  }
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## Security Considerations

1. **Keep API keys secure**: Treat API keys like passwords. Never commit them to version control or share them publicly.

2. **Use descriptive names**: Give each API key a descriptive name so you can identify its purpose later.

3. **Deactivate unused keys**: If an API key is no longer needed, deactivate it in the admin panel instead of deleting it (this preserves the audit trail).

4. **Monitor usage**: The "Last used at" field in the admin panel shows when each API key was last used.

5. **One key per application**: Create separate API keys for different applications or services. This allows you to revoke access to one service without affecting others.

6. **HTTPS only**: Always use HTTPS when transmitting API keys to prevent them from being intercepted.

## How It Works

1. The middleware checks for an Authorization header in the format `Api-Key <key>`
2. If found, it looks up the API key in the database
3. If the key exists and is active, the request.user is set to the associated user
4. The last_used_at timestamp is updated
5. The request proceeds with the authenticated user

## Permissions

When authenticated via API key, the user has all the same permissions as if they were logged in normally through the web interface. The API key simply provides an alternative authentication method.

## Troubleshooting

### API key not working

- Verify the key is active in the admin panel
- Check that the Authorization header is formatted correctly: `Api-Key <key>` (note the space after "Api-Key")
- Ensure you're using the full API key (it should be 64 characters long)

### User permissions issues

- Remember that the API key authenticates as a specific user
- The authenticated user must have the necessary permissions for the action you're trying to perform
- Check the user's groups and permissions in the admin panel

