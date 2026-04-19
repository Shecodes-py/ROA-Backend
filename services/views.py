from django.shortcuts import render, redirect #, get_object_or_404
# from django.views.generic import ListView
# from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import JsonResponse

# from rest_framework import generics
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Booking, AdditionalService, AreaChoice, ServiceChoices, PropertySizeChoice
from .serializers import BookingSerializer, BookingListSerializer, AdditionalServiceSerializer

from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Create your views here.
def home(request):
    '''Display the home page with available services.'''

    context = {
        'data': 'Welcome to the Service Booking Home Page'
    }
    return render(request, 'services.html', context)


class AdditionalServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all active add-on services with their prices.
    Used by the frontend booking form.
    """
    queryset = AdditionalService.objects.filter(is_active=True)
    serializer_class = AdditionalServiceSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_summary="List available add-ons", tags=["Bookings"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Get add-on detail", tags=["Bookings"])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class BookingViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for bookings.
    - Guests/unauthenticated users: create only.
    - Authenticated users: see and manage their own bookings.
    - Admins: see all bookings.
    """
    serializer_class = BookingSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ['list', 'retrieve', 'update', 'partial_update']:
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Booking.objects.none()
        if user.is_staff:
            return Booking.objects.all().prefetch_related('additional_services', 'payments')
        return Booking.objects.filter(user=user).prefetch_related('additional_services', 'payments')

    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        return BookingSerializer

    @swagger_auto_schema(
        operation_summary="Create a booking",
        operation_description=(
            "Create a booking. Works for guests and authenticated users. "
            "Price is always calculated server-side — do not send `total_price`."
        ),
        tags=["Bookings"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="List my bookings", tags=["Bookings"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Get booking detail", tags=["Bookings"])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update booking", tags=["Bookings"])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Cancel booking",
        tags=["Bookings"],
        responses={200: "Booking cancelled"},
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status in ['completed', 'cancelled']:
            return Response(
                {"detail": f"Cannot cancel a booking with status '{booking.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking.status = 'cancelled'
        booking.save(update_fields=['status'])
        return Response({"detail": "Booking cancelled successfully."})


@api_view(['GET'])
@permission_classes([AllowAny])
def booking_options(request):
    """
    Return all dropdown options for the booking form.

    GET /api/bookings/options/
    """
    add_ons = AdditionalService.objects.filter(is_active=True)
    return JsonResponse({
        'success': True,
        'services': [{'value': v, 'label': l} for v, l in ServiceChoices.choices],
        'property_sizes': [{'value': v, 'label': l} for v, l in PropertySizeChoice.choices],
        'add_ons': AdditionalServiceSerializer(add_ons, many=True).data,
        'areas': [{'value': v, 'label': l} for v, l in AreaChoice.choices],
    })