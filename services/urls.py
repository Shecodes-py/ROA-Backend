from django.urls import path
from .views import BookingViewSet, AdditionalServiceViewSet, home, booking_options


app_name = 'bookings'

urlpatterns = [
   path("health_check/", home, name="health_check"),
    
    # Add-ons (Read-only)
    path('Addon', AdditionalServiceViewSet.as_view({'get': 'list'}), name='additional_services_list'),
    path('Addon/<int:pk>/', AdditionalServiceViewSet.as_view({'get': 'retrieve'}), name='additional_service_detail'),
    
    # Booking Options (For dropdowns)
    path('booking-options', booking_options, name='booking_options'),
    
    # Main booking page
    #path('booking', BookingViewSet.as_view({'get': 'list'}), name='booking_page'),
    path('bookings/', BookingViewSet.as_view({'get': 'list', 'post': 'create'}), name='booking_list_create'),
    path('bookings/<int:pk>/', BookingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='booking_detail'),
    path('bookings/<int:pk>/cancel/', BookingViewSet.as_view({'post': 'cancel'}), name='booking_cancel'),
 ]

