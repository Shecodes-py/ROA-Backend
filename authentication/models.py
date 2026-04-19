from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses email as the unique identifier.
    Includes profile, address, and phone fields for the dashboard.
    """

    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone_number = models.CharField(_("phone number"), max_length=20, blank=True)

    address_line1 = models.CharField(_("address line 1"), max_length=255, blank=True)
    address_line2 = models.CharField(_("address line 2"), max_length=255, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    state = models.CharField(_("state / province"), max_length=100, blank=True)
    postal_code = models.CharField(_("postal code"), max_length=20, blank=True)
    
    # ── Dashboard / preferences ────────────────────────────────────────────────
    class NotificationPreference(models.TextChoices):
        ALL = "all", _("All notifications")
        EMAIL_ONLY = "email", _("Email only")
        NONE = "none", _("None")

    notification_preference = models.CharField(
        max_length=10,
        choices=NotificationPreference.choices,
        default=NotificationPreference.ALL,
    )
    is_email_verified = models.BooleanField(default=False)
    last_activity = models.DateTimeField(null=True, blank=True)
    profile_completion = models.PositiveSmallIntegerField(default=0)  # 0-100 %

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def full_address(self):
        parts = filter(None, [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
        ])
        return ", ".join(parts)

    def calculate_profile_completion(self):
        """Return percentage of optional profile fields filled in."""
        fields = [
            self.first_name, self.last_name, self.phone_number,
            self.avatar, self.address_line1, self.city, 
        ]
        filled = sum(1 for f in fields if f)
        self.profile_completion = int((filled / len(fields)) * 100)
        self.save(update_fields=["profile_completion"])
        return self.profile_completion