from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import time, date, timedelta
from decimal import Decimal

from services.models import (
    Service, CleaningServiceOption, PropertySizeOption,
    AdditionalService, TimeSlot, Schedule
)


class Command(BaseCommand):
    help = 'Seed initial booking system data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding booking data...')
        
        # Create Services
        self.stdout.write('Creating services...')
        services_data = [
            {
                'service_type': 'cleaning_services',
                'name': 'Residential Cleaning',
                'description': 'Professional home cleaning service',
                'base_price': Decimal('15000')
            },
            {
                'service_type': 'fumigation_services',
                'name': 'Fumigation Service',
                'description': 'Professional pest control',
                'base_price': Decimal('25000')
            },
            {
                'service_type': 'laundry_services',
                'name': 'Laundry Service',
                'description': 'Wash, fold and dry cleaning',
                'base_price': Decimal('5000')
            },
        ]
        
        for service_data in services_data:
            Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
        
        # Create Cleaning Options
        self.stdout.write('Creating cleaning options...')
        cleaning_service = Service.objects.filter(service_type='cleaning_services').first()
        if cleaning_service:
            CleaningServiceOption.objects.get_or_create(
                service=cleaning_service,
                cleaning_type='residential_cleaning',
                defaults={
                    'name': 'Residential Cleaning',
                    'description': 'Homes, apartments, condos'
                }
            )
            CleaningServiceOption.objects.get_or_create(
                service=cleaning_service,
                cleaning_type='commercial_cleaning',
                defaults={
                    'name': 'Commercial Cleaning',
                    'description': 'Offices, retail spaces'
                }
            )
        
        # Create Property Sizes
        self.stdout.write('Creating property sizes...')
        property_sizes = [
            ('small', 'Small (1-2 rooms)', Decimal('1.0')),
            ('medium', 'Medium (3-4 rooms)', Decimal('1.5')),
            ('large', 'Large (5+ rooms)', Decimal('2.0')),
            ('commercial_space', 'Commercial Space', Decimal('2.5')),
        ]
        
        for size_type, display_name, multiplier in property_sizes:
            PropertySizeOption.objects.get_or_create(
                size_type=size_type,
                defaults={
                    'display_name': display_name,
                    'price_multiplier': multiplier
                }
            )
        
        # Seed Additional Services
        self.stdout.write('Creating add-ons...')
        AdditionalService.seed_defaults()
        
        # Seed Time Slots
        self.stdout.write('Creating time slots...')
        TimeSlot.seed_slots()
        
        # Create sample schedules for next 30 days
        self.stdout.write('Creating schedules...')
        time_slots = TimeSlot.objects.all()
        today = date.today()
        
        for i in range(30):
            schedule_date = today + timedelta(days=i)
            for slot in time_slots:
                Schedule.objects.get_or_create(
                    date=schedule_date,
                    slot=slot,
                    defaults={'is_available': True}
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded booking data!'))


