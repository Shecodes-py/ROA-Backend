from django.db import models
from decimal import Decimal
from django.conf import settings

# Create your models here.
class ServiceChoices(models.TextChoices):
    CLEANING = 'cleaning services', 'Cleaning Services'
    FUMIGATION = 'fumigation services', 'Fumigation Services'
    LAUNDRY = 'laundry services', 'Laundry Services'
    

class StatusChoice(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'

class PropertySizeChoice(models.TextChoices):
    SMALL = 'small', 'Small'
    MEDIUM = 'medium', 'Medium'
    LARGE = 'large', 'Large'
    COMMERCIAL_SPACE = 'commercial space', 'Commercial Space'

class AddOnType(models.TextChoices):
    DEEP_CLEANING = 'deep_cleaning', 'Deep Cleaning (+₦5,000)'
    WINDOW_CLEANING = 'window_cleaning', 'Window Cleaning (+₦3,000)'
    CARPET_CLEANING = 'carpet_cleaning', 'Carpet Cleaning (+₦2,000)'
    EMERGENCY = 'emergency', 'Emergency Service (24/7) (+₦10,000)'

class AreaChoice(models.TextChoices):
    VICTORIA_ISLAND = "victoria-island", "Victoria Island"
    LEKKI_PHASE1 = "lekki-phase1", "Lekki Phase 1"
    LEKKI_PHASE2 = "lekki-phase2", "Lekki Phase 2"
    IKEJA_GRA = "ikeja-gra", "Ikeja GRA"
    IKOYI = "ikoyi", "Ikoyi"
    SURULERE = "surulere", "Surulere"
    YABA = "yaba", "Yaba"
    OTHER = "other", "Other"

# Base prices per service (in Naira)
BASE_PRICES = {
    ServiceChoices.CLEANING: Decimal('15000.00'),
    ServiceChoices.FUMIGATION: Decimal('20000.00'),
    ServiceChoices.LAUNDRY: Decimal('8000.00'),
}

# Property size multipliers
SIZE_MULTIPLIERS = {
    PropertySizeChoice.SMALL: Decimal('1.0'),
    PropertySizeChoice.MEDIUM: Decimal('1.5'),
    PropertySizeChoice.LARGE: Decimal('2.0'),
    PropertySizeChoice.COMMERCIAL_SPACE: Decimal('3.0'),
}

# Add-on prices
ADDON_PRICES = {
    AddOnType.DEEP_CLEANING: Decimal('5000.00'),
    AddOnType.WINDOW_CLEANING: Decimal('3000.00'),
    AddOnType.CARPET_CLEANING: Decimal('2000.00'),
    AddOnType.EMERGENCY: Decimal('10000.00'),
}


class AdditionalService(models.Model):
    """Stores extra services a customer can add to their booking."""
    addon_type = models.CharField(max_length=30, choices=AddOnType.choices, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name  # FIX: was self.name() — name is a field, not a method

    class Meta:
        ordering = ['addon_type']

# Main booking Model
class Booking(models.Model):
    """The main model to hold a customer's confirmed booking."""
    class CleaningType(models.TextChoices):
        RESIDENTIAL = 'residential', 'Residential Cleaning'
        COMMERCIAL = 'commercial', 'Commercial Cleaning'

    #  Service Selection 
    cleaning_type = models.CharField(max_length=20, choices=CleaningType.choices, null=True, blank=True)
    
    # service details
    main_service = models.CharField(default='', max_length=30, choices=ServiceChoices.choices)
    additional_services = models.ManyToManyField(AdditionalService, blank=True)
    property_size = models.CharField(default='', max_length=30, choices=PropertySizeChoice.choices)
    recurring = models.BooleanField(default=False)
    recurring_interval = models.CharField(max_length=20, blank=True, null=True)

    # user details
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='bookings')
    first_name = models.CharField(blank=True,max_length=100)
    last_name = models.CharField(blank=True,max_length=100)
    phone = models.CharField(blank=True,max_length=20) 
    email = models.EmailField(blank=True, null=True)
    description = models.TextField(max_length=255, null=True, blank=True)

    # schedule details
    service_date = models.DateField( null=True, blank=True)
    
    # location
    address = models.TextField(default='', blank=True)
    location = models.CharField(default='', max_length=30, choices=AreaChoice.choices)
    special_instructions = models.TextField(blank=True)
    
    # pricing
    # ── Pricing (all computed server-side) ────────────────────────────────────
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    addons_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # META
    status = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        # FIX: main_service is a CharField value, not a FK object
        name = f"{self.first_name} {self.last_name}".strip() or (
            self.user.email if self.user else "Guest"
        )
        return f"Booking #{self.pk} — {name} ({self.get_main_service_display()})"


    @property
    def customer_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def calculate_price(self):
        """
        Compute base_price, addons_total, and total_price server-side.
        Call this before saving when add-ons are already set.
        """
        base = BASE_PRICES.get(self.main_service, Decimal('0.00'))
        multiplier = SIZE_MULTIPLIERS.get(self.property_size, Decimal('1.0'))
        self.base_price = base * multiplier

        addon_sum = sum(
            ADDON_PRICES.get(addon.addon_type, Decimal('0.00'))
            for addon in self.additional_services.all()
        )
        self.addons_total = addon_sum
        self.total_price = self.base_price + self.addons_total
        return self.total_price

    def get_total_price(self):
        return self.total_price
