from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

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

class AdditionalService(models.Model):
    """Stores extra services (e.g., Deep Cleaning, Window Cleaning)."""
    addon_type = models.CharField(max_length=30, choices=AddOnType.choices, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    addon_deep_cleaning = models.BooleanField(default=False)
    addon_window_cleaning = models.BooleanField(default=False)
    addon_carpet_cleaning = models.BooleanField(default=False)
    is_emergency = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name()}"

# Main booking Model
class Booking(models.Model):
    """The main model to hold a customer's confirmed booking."""
    class CleaningType(models.TextChoices):
        RESIDENTIAL = 'residential', 'Residential Cleaning'
        COMMERCIAL = 'commercial', 'Commercial Cleaning'

    # --- Service Selection ---
    cleaning_type = models.CharField(max_length=20, choices=CleaningType.choices, null=True, blank=True)
    
    # service details
    main_service = models.CharField(default='', max_length=30, choices=ServiceChoices.choices)
    additional_services = models.ManyToManyField(AdditionalService, blank=True)
    property_size = models.CharField(default='', max_length=30, choices=PropertySizeChoice.choices)
    recurring = models.BooleanField(default=False)
    recurring_interval = models.CharField(max_length=20, blank=True, null=True)

    # user details
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bookings')
    first_name = models.CharField(blank=True,max_length=100)
    last_name = models.CharField(blank=True,max_length=100)
    phone = models.CharField(blank=True,max_length=20)
    email = models.EmailField(blank=True, null=True)
    description = models.TextField(blank=True)
    
    # schedule details
    service_date = models.DateField(default=None, null=True, blank=True)
    
    # location
    address = models.TextField(default='', blank=True)
    location = models.CharField(default='', max_length=30, choices=AreaChoice.choices)
    special_instructions = models.TextField(blank=True)
    
    # pricing
    base_price = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    # property_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    # add_ons_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    # emergency_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_price = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)

    # META
    status = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # payment
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    payment_method = models.CharField(default='debit_card', max_length=20, choices=PAYMENT_METHODS)

    
    def get_total_price(self):
        pass

    def __str__(self):
        return f"Booking by {self.user.username} for {self.main_service.service_type}"
    
    def calculate_price(self):
        pass
    
    def save(self, *args, **kwargs):
        pass