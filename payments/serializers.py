from rest_framework import serializers
from .models import Payment, PaymentReceipt

# write your serializers here
class InitiatePaymentSerializer(serializers.Serializer):
    """Request body for initiating a Paystack payment."""
    booking_id = serializers.IntegerField(help_text="ID of the booking to pay for.")


class PaymentSerializer(serializers.ModelSerializer):
    booking_reference = serializers.CharField(source='booking.id', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'booking_reference',
            'reference', 'paystack_transaction_id',
            'amount', 'currency',
            'status', 'gateway_response', 'channel',
            'paid_at', 'created_at',
        ]
        read_only_fields = fields


class PaymentReceiptSerializer(serializers.ModelSerializer):
    payment_reference = serializers.CharField(source='payment.reference', read_only=True)
    payment_channel = serializers.CharField(source='payment.channel', read_only=True)

    class Meta:
        model = PaymentReceipt
        fields = [
            'id', 'receipt_number',
            'payment_reference', 'payment_channel',
            'customer_name', 'customer_email',
            'service_description', 'amount_paid',
            'issued_at',
        ]
        read_only_fields = fields


class VerifyPaymentSerializer(serializers.Serializer):
    """Request body to manually verify a payment by reference."""
    reference = serializers.CharField(
        help_text="The payment reference returned from the initiate endpoint."
    )