from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Service(models.Model):
    SERVICE_TYPES = [
        ('cleaning services', 'Cleaning Services'),
        ('fumigation services', 'Fumigation Services'),
        ('laundry services', 'Laundry Services'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.service_type} booked by {self.user.username}"

class PropertySize(models.TextChoices):
    SMALL = 'small', 'Small'
    MEDIUM = 'medium', 'Medium'
    LARGE = 'large', 'Large'
    COMMERCIAL_SPACE = 'commercial space', 'Commercial Space'

class CleaningServiceOption(models.Model):               
    CLEANING_TYPE = [
        ('residential cleaning', 'Residential Cleaning'),
        ('commercial cleaning', 'Commercial Cleaning'),
    ]
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='cleaning_services')  
    cleaning_type = models.CharField(max_length=30, choices=CLEANING_TYPE)
    property_size = models.CharField(max_length=30, choices=PropertySize.choices)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['service', 'cleaning_type', 'property_size'], 
                name='unique_cleaning_service_option')
        ]

    def __str__(self):
        return f"{self.cleaning_type} - {self.property_size}"
    
class FumigationServiceOption(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='fumigation_services')
    property_size = models.CharField(max_length=30, choices=PropertySize.choices)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['service', 'property_size'], 
                name='unique_fumigation_service_option')
        ]

    def __str__(self):
        return f"{self.service.name} - {self.property_size}"

class LaundryServiceOption(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='laundry_services')
    # this could be extended with more specific laundry options in the future
    def __str__(self):
        return f"{self.service.name} Laundry Option"

class AddOnType(models.TextChoices):
    DEEP_CLEANING = 'deep_cleaning', 'Deep Cleaning (+₦5,000)'
    WINDOW_CLEANING = 'window_cleaning', 'Window Cleaning (+₦3,000)'
    CARPET_CLEANING = 'carpet_cleaning', 'Carpet Cleaning (+₦2,000)'
    EMERGENCY = 'emergency', 'Emergency Service (24/7) (+₦10,000)'

class AdditionalService(models.Model):
    """Stores extra services (e.g., Deep Cleaning, Window Cleaning)."""
    addon_type = models.CharField(max_length=30, choices=AddOnType.choices, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    
    @staticmethod # run this once to populate database table
    def seed_defaults(): 
        defaults = {
            AddOnType.DEEP_CLEANING: 5000.00,
            AddOnType.WINDOW_CLEANING: 3000.00,
            AddOnType.CARPET_CLEANING: 2000.00,
            AddOnType.EMERGENCY: 10000.00,
        }
        for addon, price in defaults.items():
            AdditionalService.objects.get_or_create(addon_type=addon, defaults={'price': price})

    def __str__(self):
        return f"{self.get_addon_type_display()}"

class TimeSlot(models.TextChoices):
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    # seed this once to populate database table # run with TimeSlot.seed_slots()
    @staticmethod
    def seed_slots():
        slots = [
            ("08:00", "10:00"),
            ("10:00", "12:00"),
            ("14:00", "16:00"),
            ("16:00", "18:00"),
        ]
        for start, end in slots: TimeSlot.objects.get_or_create(
                start_time=start,
                defaults={'end_time': end}
            )
    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
    
class Schedule(models.Model):
    """Model to hold available scheduling dates for services."""
    date = models.DateField()
    slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('date', 'slot')

    def __str__(self):
        return f"{self.date} - {self.slot}"

class ServiceLocation(models.Model):
    """Model to hold service location details."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_locations')
    address_line = models.CharField(max_length=255)
    area = models.CharField(max_length=100)
    # city = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.country}"

# Main booking Model
class Booking(models.Model):
    """The main model to hold a customer's confirmed booking."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    main_service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='bookings')
    additional_services = models.ManyToManyField(AdditionalService, blank=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT, related_name='bookings')
    booked_at = models.DateTimeField(auto_now_add=True) 

    def total_price(self):
        pass  # Implementation of total price calculation goes here
    
    def __str__(self):
        return f"Booking by {self.user.username} for {self.main_service.service_type}"

class RecurringBooking(models.Model):
    """Model to handle recurring bookings."""
    INTERVAL_CHOICES = [
        ('weekly', 'Weekly'),
        ('bi_weekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    # Upcoming fields to be added for recurring bookings
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_bookings')