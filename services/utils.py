'''
FIXED_PRICES = {
        ('cleaning services', 'residential', 'small'): 15000.00,
        ('cleaning services', 'residential', 'medium'): 22500.00,
        ('cleaning services', 'residential', 'large'): 30000.00,
        ('cleaning services', 'commercial', 'small'): 37500.00,
        ('cleaning services', 'commercial', 'medium'): 50000.00,
        ('cleaning services', 'commercial', 'large'): 80000.00,
        ('cleaning services', 'commercial', 'commercial_space'): 100000.00,

        # Fumigation Services
        ('fumigation services', None, 'small'): 25000.00,
        ('fumigation services', None, 'medium'): 35000.00,
        ('fumigation services', None, 'large'): 55000.00,
        ('fumigation services', None, 'commercial_space'): 150000.00,
        
        # Laundry Services
        ('laundry services', None, None): 5000.00,  # per load
    }

@classmethod
def get_price(self, service_subtype=None, property_size=None):
        """Retrieve fixed price based on service type, subtype, and property size."""
        key = (self.service_type.split()[0], service_subtype, property_size)
        return self.FIXED_PRICES.get(key, self.base_price)

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
        return f"{self.service.service_type} - {self.property_size}"

class LaundryServiceOption(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='laundry_services')
    # this could be extended with more specific laundry options in the future
    def __str__(self):
        return f"{self.service.service_type} Laundry Option"






class Area(models.Model):
    """Service areas/districts"""
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class Booking(models.Model):
    """Main booking model"""
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('pi_crypto', 'Pi Cryptocurrency'),
        ('cash', 'Cash on Service'),
    ]
    
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('bi_weekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Service Details
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='bookings')
    cleaning_type = models.ForeignKey(CleaningType, on_delete=models.SET_NULL, null=True, blank=True)
    property_size = models.ForeignKey(PropertySize, on_delete=models.PROTECT)
    add_ons = models.ManyToManyField(ServiceAddOn, blank=True, related_name='bookings')
    is_emergency = models.BooleanField(default=False)
    
    # Schedule Details
    service_date = models.DateField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT)
    
    # Recurring Service
    is_recurring = models.BooleanField(default=False)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, null=True, blank=True)
    
    # Contact Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Location
    address = models.TextField()
    area = models.ForeignKey(Area, on_delete=models.PROTECT)
    special_instructions = models.TextField(blank=True)
    
    # Payment & Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    add_ons_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    emergency_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # Status & Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    terms_agreed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def calculate_total(self):
        """Calculate the total booking amount"""
        # Base price with property size multiplier
        total = self.base_price * self.property_size.price_multiplier
        
        # Add-ons
        total += self.add_ons_total
        
        # Emergency service fee
        if self.is_emergency:
            total += Decimal('10000')
        
        # Recurring discount (15% off)
        if self.is_recurring:
            total = total * Decimal('0.85')
        
        return total
    
    def save(self, *args, **kwargs):
        """Override save to calculate total before saving"""
        # Calculate add-ons total
        if self.pk:  # Only if booking already exists
            self.add_ons_total = sum(addon.price for addon in self.add_ons.all())
        
        # Set emergency fee
        self.emergency_fee = Decimal('10000') if self.is_emergency else Decimal('0')
        
        # Calculate total
        self.total_amount = self.calculate_total()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Booking #{self.id} - {self.first_name} {self.last_name} - {self.service_date}"'''