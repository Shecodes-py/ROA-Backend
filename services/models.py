from django.db import models
from decimal import Decimal
from django.conf import settings
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

# Create your models here.
class ServiceChoices(models.TextChoices):
    CLEANING = 'cleaning', 'Cleaning Services'
    FUMIGATION = 'fumigation', 'Fumigation Services'
    LAUNDRY = 'laundry', 'Laundry Services'
    

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
    FLAT = 'flat', 'Flat'
    LARGE_AREA = 'large_area', 'Large Area'
    
class CleaningTypeChoice(models.TextChoices):
    RESIDENTIAL = 'residential', 'Residential Cleaning'
    COMMERCIAL = 'commercial', 'Commercial Cleaning'
    
class AddOnType(models.TextChoices):
    DEEP_CLEANING = 'deep_cleaning', 'Deep Cleaning (+₦5,000)'
    WINDOW_CLEANING = 'window_cleaning', 'Window Cleaning (+₦3,000)'
    CARPET_CLEANING = 'carpet_cleaning', 'Carpet Cleaning (+₦2,000)'
    # EMERGENCY = 'emergency', 'Emergency Service (24/7) (+₦10,000)'

class AreaChoice(models.TextChoices):
    VICTORIA_ISLAND = "victoria_island", "Victoria Island"
    LEKKI_PHASE1 = "lekki-phase1", "Lekki Phase 1"
    LEKKI_PHASE2 = "lekki-phase2", "Lekki Phase 2"
    IKEJA_GRA = "ikeja-gra", "Ikeja GRA"
    IKOYI = "ikoyi", "Ikoyi"
    SURULERE = "surulere", "Surulere"
    YABA = "yaba", "Yaba"
    OTHER = "other", "Other"

EMERGENCY_FEE = Decimal('10000.00')

# Base prices per service (in Naira)
BASE_PRICES = {
    'cleaning': Decimal('15000.00'),
    'fumigation': Decimal('20000.00'),
    'laundry': Decimal('8000.00'),
}

# Property size multipliers
SIZE_MULTIPLIERS = {
    'small': Decimal('1.0'),
    'medium': Decimal('1.5'),
    'large': Decimal('2.0'),
}

# Add-on prices
ADDON_PRICES = {
    AddOnType.DEEP_CLEANING: Decimal('5000.00'),
    AddOnType.WINDOW_CLEANING: Decimal('3000.00'),
    AddOnType.CARPET_CLEANING: Decimal('2000.00'),
    # AddOnType.EMERGENCY: Decimal('10000.00'),
}
# Add-on prices are stored on AdditionalService.price (DB is the single source of truth).
# Prices are aggregated via additional_services.aggregate() in Booking.calculate_price().


class AdditionalService(models.Model):
    """Stores extra services a customer can add to their booking."""
    addon_type = models.CharField(max_length=30, choices=AddOnType.choices, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name  
    
    class Meta:
        ordering = ['addon_type']

# Main booking Model
class Booking(models.Model):
    """The main model to hold a customer's confirmed booking."""

    # service details
    main_service = models.CharField(default='', max_length=50, choices=ServiceChoices.choices)
    
    #  Service Selection 
    cleaning_type = models.CharField(max_length=20, choices=CleaningTypeChoice.choices, null=True, blank=True)
    property_size = models.CharField(max_length=50, choices=PropertySizeChoice.choices,blank=True, null=True, default=None)
    
    additional_services = models.ManyToManyField(AdditionalService, blank=True)
    
    # new fields for emergency and recurring
    is_emergency = models.BooleanField(default=False)
    time_slot = models.CharField(max_length=20, blank=True, null=True)  # e.g., "Morning", "Afternoon", "Evening"
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Card", "Cash", "Mobile Money"
    
    is_recurring = models.BooleanField(default=False)
    recurring_interval = models.CharField(max_length=20, blank=True, null=True)

    # user details
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='bookings')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20) 
    email = models.EmailField(null=True)
    description = models.TextField(max_length=255, null=True, blank=True)

    # schedule details
    service_date = models.DateField( null=True, blank=True)
    
    # location
    address = models.TextField(default='', blank=True)
    location = models.CharField(default='', max_length=30)
    special_instructions = models.TextField(blank=True)
    
    # pricing
    # ── Pricing (all computed server-side) ────────────────────────────────────
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    addons_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    emergency_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # META
    status = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.pk} - {self.first_name} ({self.main_service})"
    

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

        if self.pk:
            self.addons_total = self.additional_services.aggregate(
                total=models.Sum('price')            )['total'] or Decimal('0.00')
        else:
            self.addons_total = Decimal('0.00')

        self.emergency_charge = EMERGENCY_FEE if self.is_emergency else Decimal('0.00')

        self.total_price = self.base_price + self.addons_total + self.emergency_charge
        
        return self.total_price

    def get_total_price(self):
        return self.total_price
    
    def save(self, *args, **kwargs):
        # Ensure price is calculated before saving
        # is_new = self.pk is None
        self.calculate_price()
        super().save(*args, **kwargs)
        

        # Booking.objects.filter(pk=self.pk).update(
        #     base_price=self.base_price,
        #     addons_total=self.addons_total,
        #     emergency_charge=self.emergency_charge,
        #     total_price=self.total_price
        # )

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.main_service == ServiceChoices.CLEANING and not self.cleaning_type:
            raise ValidationError("Cleaning type is required when main service is Cleaning.")



@receiver(m2m_changed, sender=Booking.additional_services.through)
def recalculate_price_on_addon_change(sender, instance, action, **kwargs):
    """Recalculate price whenever additional_services M2M is modified."""
    if action in ('post_add', 'post_remove', 'post_clear'):
        instance.calculate_price()
        Booking.objects.filter(pk=instance.pk).update(
            base_price=instance.base_price,
            addons_total=instance.addons_total,
            emergency_charge=instance.emergency_charge,
            total_price=instance.total_price,
        )