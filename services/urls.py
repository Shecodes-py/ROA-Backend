from django.urls import path
from .views import BookingViewSet, AdditionalServiceViewSet, home, booking_options

app_name = 'bookings'

booking_list   = BookingViewSet.as_view({'get': 'list',   'post': 'create'})
booking_detail = BookingViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})

addon_list   = AdditionalServiceViewSet.as_view({'get': 'list'})
addon_detail = AdditionalServiceViewSet.as_view({'get': 'retrieve'})

urlpatterns = [
    path('health/', home, name='health_check'),
    
    # Main booking page
    path('bookings/',          booking_list,   name='booking-list'),
    path('bookings/<int:pk>/', booking_detail, name='booking-detail'),
    path('bookings/<int:pk>/cancel/', BookingViewSet.as_view({'post': 'cancel'}), name='booking-cancel'),

    path('Addon/',          addon_list,   name='addon-list'),
    path('Addon/<int:pk>/', addon_detail, name='addon-detail'),

    path('booking-options/', booking_options, name='booking-options'),
]

