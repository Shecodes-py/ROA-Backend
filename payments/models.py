from django.db import models
from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid

# Create your models here.
class Payment(models.Model):
    """
    Records a single payment attempt against a booking.
    One booking can have multiple attempts (e.g. first fails, second succeeds).
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'
        ABANDONED = 'abandoned', 'Abandoned'
        REVERSED = 'reversed', 'Reversed'

    class Currency(models.TextChoices):
        NGN = 'NGN', 'Nigerian Naira'
        USD = 'USD', 'US Dollar'

    # booking = models.ForeignKey(
    #     'bookings.Booking',
    #     on_delete=models.PROTECT,
    #     related_name='payments',
    # )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payments',
    )

    # Our internal reference sent to Paystack
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    # Paystack's own transaction ID returned after verification
    paystack_transaction_id = models.CharField(max_length=100, blank=True, db_index=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.NGN
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    gateway_response = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    channel = models.CharField(max_length=50, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.reference} — ₦{self.amount} ({self.status})"

    @property
    def amount_in_kobo(self):
        """Paystack expects amounts in kobo (1 NGN = 100 kobo)."""
        return int(self.amount * 100)

    @classmethod
    def generate_reference(cls):
        """Generates a unique ROA-prefixed reference."""
        return f"ROA-{uuid.uuid4().hex[:12].upper()}"


class PaymentReceipt(models.Model):
    """
    A human-readable receipt generated after a successful payment.
    One-to-one with a successful Payment.
    """
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='receipt',
    )
    receipt_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    # Snapshot of booking details at time of payment (in case booking is updated later)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    service_description = models.TextField()
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"Receipt {self.receipt_number} — {self.customer_name}"

    @classmethod
    def generate_receipt_number(cls):
        return f"REC-{uuid.uuid4().hex[:8].upper()}"