from django.contrib import admin
from django.contrib import admin
from .models import Payment, PaymentReceipt

# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'reference', 'booking', 'amount', 'currency',
        'status', 'channel', 'paid_at', 'created_at',
    ]
    list_filter = ['status', 'currency', 'channel', 'created_at']
    search_fields = ['reference', 'paystack_transaction_id', 'booking__id', 'user__email']
    readonly_fields = [
        'reference', 'paystack_transaction_id', 'amount',
        'currency', 'status', 'gateway_response',
        'channel', 'metadata', 'paid_at', 'created_at', 'updated_at',
    ]
    ordering = ['-created_at']


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = [
        'receipt_number', 'customer_name', 'customer_email',
        'amount_paid', 'issued_at',
    ]
    search_fields = ['receipt_number', 'customer_name', 'customer_email']
    readonly_fields = [
        'receipt_number', 'payment', 'customer_name', 'customer_email',
        'service_description', 'amount_paid', 'issued_at',
    ]
    ordering = ['-issued_at']