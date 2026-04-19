from django.urls import path
from .views import BookingViewSet, AdditionalServiceViewSet, home, booking_options


app_name = 'bookings'

urlpatterns = [
   path("health_check/", home, name="health_check"),
    
    # Main booking page
    path('booking', BookingViewSet.as_view({'get': 'list'}), name='booking_page'),
    path('Addon', AdditionalServiceViewSet.as_view({'get': 'list'}), name='additional_services_list'),
    path('Addon/<int:pk>/', AdditionalServiceViewSet.as_view({'get': 'retrieve'}), name='additional_service_detail'),
    path('booking-options', booking_options, name='booking_options'),
   
]