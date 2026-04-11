from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, AdditionalServiceViewSet
from . import views

# router = DefaultRouter()
# router.register(r'bookings', BookingViewSet)
# router.register(r'add-ons', AdditionalServiceViewSet)


app_name = 'bookings'

urlpatterns = [
    # path('api/', include(router.urls)),

    # Main booking page
    path('', views.BookingViewSet.as_view({'get': 'list'}), name='booking_page'),
    
    # API Endpoints for Frontend Form
    # path('api/create/', views.create_booking_api, name='create_booking'),
    # path('api/options/', views.get_booking_options, name='get_options'),
    # path('api/availability/', views.check_availability, name='check_availability'),
    # path('api/available-dates/', views.get_available_dates, name='available_dates'),
    
    # # Booking Management API
    # path('api/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    # path('api/', views.BookingListView.as_view(), name='booking_list'),
    # path('api/my-bookings/', views.UserBookingsView.as_view(), name='user_bookings'),
    # path('api/<int:booking_id>/status/', views.update_booking_status, name='update_status'),
    
    # # Success page
    # path('success/<int:booking_id>/', views.booking_success, name='booking_success'),
]