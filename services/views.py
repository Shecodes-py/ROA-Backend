from django.shortcuts import render, redirect #, get_object_or_404
# from django.views.generic import ListView
# from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import JsonResponse

# from rest_framework import generics
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Booking, AdditionalService
from .serializers import BookingSerializer, AdditionalServiceSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# Create your views here.
def home(request):
    '''Display the home page with available services.'''

    context = {
        'data': 'Welcome to the Service Booking Home Page'
    }
    return render(request, 'services.html', context)

class AdditionalServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint to let the front-end fetch available add-ons and their prices.
    """
    queryset = AdditionalService.objects.filter(is_active=True)
    serializer_class = AdditionalServiceSerializer

class BookingViewSet(viewsets.ModelViewSet):
    """
    Endpoint for creating and managing bookings.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Logic for custom price validation could go here
            booking = serializer.save()
            
            # If the user is logged in, associate the booking automatically
            if request.user.is_authenticated:
                booking.user = request.user
                booking.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_booking_data(request):
    """
    Get all available booking options for the frontend
    
    GET /api/bookings/options/
    
    Response:
    {
        "success": true,
        "services": [...],
        "property_sizes": [...],
        "add_ons": [...],
        "time_slots": [...],
        "areas": [...]
    }
    """
    services = Booking.SERVICE_TYPE_CHOICES
    property_sizes = Booking.PROPERTY_SIZE_CHOICES
    add_ons = AdditionalService.objects.filter(is_active=True)
                   
    return JsonResponse({
        'success': True,
        'services': '',
        'property_sizes': '',
        'add_ons': AdditionalServiceSerializer(add_ons, many=True).data,
        'time_slots': '',
        'areas': [
            {'value': 'victoria-island', 'label': 'Victoria Island'},
            {'value': 'lekki-phase1', 'label': 'Lekki Phase 1'},
            {'value': 'lekki-phase2', 'label': 'Lekki Phase 2'},
            {'value': 'ikeja-gra', 'label': 'Ikeja GRA'},
            {'value': 'ikoyi', 'label': 'Ikoyi'},
            {'value': 'surulere', 'label': 'Surulere'},
            {'value': 'yaba', 'label': 'Yaba'},
            {'value': 'other', 'label': 'Other'}
        ]
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    """
    Create a new booking from the frontend form
    
    POST /api/bookings/create/
    
    Request Body:
    {
        "service_type": "cleaning",
        "cleaning_type": "residential",
        "property_size": "medium",
        "add_ons": ["deep_cleaning", "window_cleaning"],
        "is_emergency": false,
        "date": "2025-12-25",
        "time": "10:00",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+234 123 456 7890",
        "email": "john@example.com",
        "address": "123 Main St",
        "area": "victoria-island",
        "special_instructions": "Call before arriving",
        "is_recurring": false,
        "frequency": "weekly",
        "payment_method": "card"
    }
    
    Response:
    {
        "success": true,
        "booking_id": 1,
        "message": "Booking confirmed! Your booking ID is #1",
        "data": {
            "booking_id": 1,
            "customer_name": "John Doe",
            "service": "Residential Cleaning",
            "date": "2025-12-25",
            "time": "8:00 AM - 10:00 AM",
            "total_amount": 22500.0,
            "status": "pending"
        }
    }
    """
    serializer = BookingSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            booking = serializer.save()
            response_data = {
                "success": True,
                "booking_id": booking.id,
                "message": f"Booking confirmed! Your booking ID is #{booking.id}",
                "data": {
                    "booking_id": booking.id,
                    "customer_name": f"{booking.first_name} {booking.last_name}",
                    "service": booking.get_service_display(),
                    "date": booking.date,
                    "time": booking.time,
                    "total_amount": booking.total_price,
                    "status": booking.status,
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

