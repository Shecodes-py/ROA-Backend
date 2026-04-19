from django.shortcuts import render
import json
import logging
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from services.models import Booking, StatusChoice
from .models import Payment, PaymentReceipt
from .paystack import PaystackService
from .serializers import (
    InitiatePaymentSerializer,
    PaymentSerializer,
    PaymentReceiptSerializer,
    VerifyPaymentSerializer,
)

logger = logging.getLogger(__name__)
paystack = PaystackService()


# Create your views here.
class InitiatePaymentView(APIView):
    """
    Start a Paystack payment for a booking.

    Returns a `authorization_url` — redirect the user there to complete payment.
    Also returns the `reference` which you must store to verify later.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Initiate payment",
        operation_description=(
            "Creates a pending Payment record and calls Paystack to get a checkout URL. "
            "Redirect your user to `authorization_url` to complete payment."
        ),
        request_body=InitiatePaymentSerializer,
        responses={
            200: openapi.Response(
                "Payment initiated",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "reference": openapi.Schema(type=openapi.TYPE_STRING),
                        "authorization_url": openapi.Schema(type=openapi.TYPE_STRING),
                        "access_code": openapi.Schema(type=openapi.TYPE_STRING),
                        "amount": openapi.Schema(type=openapi.TYPE_NUMBER),
                    }
                )
            ),
            400: "Validation error or booking already paid",
            404: "Booking not found",
        },
        tags=["Payments"],
    )
    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking_id = serializer.validated_data['booking_id']

        # Fetch booking — users can only pay for their own bookings
        try:
            booking = Booking.objects.get(
                id=booking_id,
                user=request.user,
            )
        except Booking.DoesNotExist:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Guard: don't allow double payment
        if booking.payments.filter(status=Payment.Status.SUCCESS).exists():
            return Response(
                {"detail": "This booking has already been paid for."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a pending Payment record
        reference = Payment.generate_reference()
        payment = Payment.objects.create(
            booking=booking,
            user=request.user,
            reference=reference,
            amount=booking.total_price,
            metadata={
                "booking_id": booking.id,
                "service": booking.main_service,
                "customer": booking.customer_name,
            }
        )

        # Call Paystack
        email = request.user.email or booking.email
        result = paystack.initialize_transaction(
            email=email,
            amount_kobo=payment.amount_in_kobo,
            reference=reference,
            metadata=payment.metadata,
        )

        if not result.get('status'):
            payment.status = Payment.Status.FAILED
            payment.gateway_response = result.get('message', 'Unknown error')
            payment.save(update_fields=['status', 'gateway_response'])
            return Response(
                {"detail": result.get('message', 'Payment initialization failed.')},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        data = result['data']
        return Response({
            "reference": reference,
            "authorization_url": data['authorization_url'],
            "access_code": data['access_code'],
            "amount": float(booking.total_price),
        }, status=status.HTTP_200_OK)


class VerifyPaymentView(APIView):
    """
    Verify a payment after the user returns from Paystack's checkout page.

    Call this with the `reference` you got from the initiate endpoint.
    On success, the booking status is updated to `confirmed`.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Verify payment",
        operation_description=(
            "Calls Paystack's verify endpoint. On success: marks the payment as successful, "
            "updates the booking status to `confirmed`, and generates a receipt."
        ),
        request_body=VerifyPaymentSerializer,
        responses={
            200: PaymentSerializer,
            400: "Payment failed or already verified",
            404: "Reference not found",
        },
        tags=["Payments"],
    )
    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reference = serializer.validated_data['reference']

        try:
            payment = Payment.objects.select_related('booking').get(
                reference=reference,
                user=request.user,
            )
        except Payment.DoesNotExist:
            return Response({"detail": "Payment reference not found."}, status=status.HTTP_404_NOT_FOUND)

        if payment.status == Payment.Status.SUCCESS:
            return Response(
                {"detail": "Payment already verified.", "payment": PaymentSerializer(payment).data},
                status=status.HTTP_200_OK,
            )

        # Ask Paystack
        result = paystack.verify_transaction(reference)

        if not result.get('status'):
            return Response(
                {"detail": result.get('message', 'Verification failed.')},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        data = result['data']
        paystack_status = data.get('status')  # 'success', 'failed', 'abandoned'

        payment.paystack_transaction_id = str(data.get('id', ''))
        payment.gateway_response = data.get('gateway_response', '')
        payment.channel = data.get('channel', '')
        payment.metadata = data.get('metadata', {})

        if paystack_status == 'success':
            payment.status = Payment.Status.SUCCESS
            payment.paid_at = timezone.now()
            payment.save()

            # Update booking status
            booking = payment.booking
            booking.status = StatusChoice.CONFIRMED
            booking.save(update_fields=['status'])

            # Generate receipt (idempotent)
            _create_receipt(payment, booking)

            return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

        # Payment was not successful
        payment.status = (
            Payment.Status.ABANDONED if paystack_status == 'abandoned'
            else Payment.Status.FAILED
        )
        payment.save()
        return Response(
            {"detail": f"Payment {paystack_status}. Please try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(APIView):
    """
    Paystack webhook receiver.

    Configure this URL in your Paystack dashboard:
    `https://yourdomain.com/api/payments/webhook/`

    Paystack signs each request with HMAC-SHA512 using your secret key.
    We verify the signature before processing anything.
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Webhooks don't carry user tokens

    @swagger_auto_schema(
        operation_summary="Paystack webhook (internal)",
        operation_description=(
            "Receives and processes Paystack event notifications. "
            "Not for direct client use — configure in Paystack dashboard."
        ),
        tags=["Payments"],
    )
    def post(self, request):
        # 1. Verify signature
        signature = request.headers.get('x-paystack-signature', '')
        payload = request.body

        if not paystack.verify_webhook_signature(payload, signature):
            logger.warning("Paystack webhook: invalid signature")
            return Response({"detail": "Invalid signature."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Parse event
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            return Response({"detail": "Invalid JSON."}, status=status.HTTP_400_BAD_REQUEST)

        event_type = event.get('event')
        data = event.get('data', {})

        logger.info(f"Paystack webhook received: {event_type}")

        # 3. Handle events
        if event_type == 'charge.success':
            _handle_charge_success(data)

        elif event_type == 'charge.failed':
            _handle_charge_failed(data)

        elif event_type == 'refund.processed':
            _handle_refund(data)

        # Always return 200 — Paystack retries on non-2xx
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


def _handle_charge_success(data: dict):
    reference = data.get('reference')
    if not reference:
        return

    try:
        payment = Payment.objects.select_related('booking').get(reference=reference)
    except Payment.DoesNotExist:
        logger.error(f"Webhook: payment not found for reference {reference}")
        return

    if payment.status == Payment.Status.SUCCESS:
        return  # Already processed, skip

    payment.status = Payment.Status.SUCCESS
    payment.paid_at = timezone.now()
    payment.paystack_transaction_id = str(data.get('id', ''))
    payment.gateway_response = data.get('gateway_response', '')
    payment.channel = data.get('channel', '')
    payment.metadata = data.get('metadata', {})
    payment.save()

    booking = payment.booking
    booking.status = StatusChoice.CONFIRMED
    booking.save(update_fields=['status'])

    _create_receipt(payment, booking)
    logger.info(f"Webhook: payment {reference} confirmed via webhook")


def _handle_charge_failed(data: dict):
    reference = data.get('reference')
    if not reference:
        return
    Payment.objects.filter(reference=reference, status=Payment.Status.PENDING).update(
        status=Payment.Status.FAILED,
        gateway_response=data.get('gateway_response', 'Failed'),
    )


def _handle_refund(data: dict):
    # Placeholder for refund handling
    logger.info(f"Refund processed: {data}")


def _create_receipt(payment: Payment, booking) -> PaymentReceipt:
    """Create a PaymentReceipt if one doesn't already exist."""
    receipt, created = PaymentReceipt.objects.get_or_create(
        payment=payment,
        defaults={
            "receipt_number": PaymentReceipt.generate_receipt_number(),
            "customer_name": booking.customer_name,
            "customer_email": booking.email,
            "service_description": (
                f"{booking.get_main_service_display()} — "
                f"{booking.get_property_size_display()} property at "
                f"{booking.get_location_display()}"
            ),
            "amount_paid": payment.amount,
        }
    )
    return receipt

class PaymentHistoryView(generics.ListAPIView):
    """
    List all payments made by the authenticated user,
    most recent first.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related('booking')

    @swagger_auto_schema(
        operation_summary="My payment history",
        tags=["Payments"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)



class PaymentReceiptView(generics.RetrieveAPIView):
    """
    Retrieve a payment receipt by its receipt number.
    Only accessible to the owner of the payment.
    """
    serializer_class = PaymentReceiptSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'receipt_number'

    def get_queryset(self):
        return PaymentReceipt.objects.filter(
            payment__user=self.request.user
        ).select_related('payment')

    @swagger_auto_schema(
        operation_summary="Get receipt",
        operation_description="Retrieve a receipt by its receipt number (e.g. REC-ABCD1234).",
        tags=["Payments"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)