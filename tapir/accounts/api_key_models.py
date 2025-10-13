import secrets
from django.db import models
from django.utils.translation import gettext_lazy as _


class APIKey(models.Model):
    """
    API Key model for authenticating requests as a specific user.
    """
    key = models.CharField(
        _("API Key"),
        max_length=64,
        unique=True,
        editable=False,
        help_text=_("The API key used for authentication"),
    )
    user = models.ForeignKey(
        "accounts.TapirUser",
        on_delete=models.CASCADE,
        related_name="api_keys",
        verbose_name=_("User"),
        help_text=_("The user this API key authenticates as"),
    )
    name = models.CharField(
        _("Name"),
        max_length=100,
        help_text=_("A descriptive name for this API key (e.g., 'Mobile App', 'External Service')"),
    )
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
    )
    last_used_at = models.DateTimeField(
        _("Last used at"),
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        _("Is active"),
        default=True,
        help_text=_("Whether this API key is currently active and can be used for authentication"),
    )

    class Meta:
        verbose_name = _("API Key")
        verbose_name_plural = _("API Keys")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.user.username}) - {self.key[:8]}..."

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """
        Generate a secure random API key.
        """
        return secrets.token_urlsafe(48)  # 48 bytes = 64 character URL-safe string

    def matches(self, key: str) -> bool:
        """
        Check if the provided key matches this API key.
        """
        return self.key == key

