from django.db import models

# Create your models here.
class Service(models.Model):
    SERVICE_TYPES = [
        ('cleaning', 'Residential Cleaning'),
        ('commercial', 'Commercial Cleaning'),
        ('fumigation', 'Fumigation'),
        ('laundry', 'Laundry'),
        ('office', 'Office Cleaning'),
    ]

    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_hours = models.IntegerField(help_text="Duration in hours")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['service_type', 'name']

    def __str__(self):
        return self.name    

class ServicePricing(models.Model):
    service = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='pricing')
    area_size_min = models.IntegerField(help_text="Minimum area size in sqm")
    area_size_max = models.IntegerField(help_text="Maximum area size in sqm")
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service.name} pricing"