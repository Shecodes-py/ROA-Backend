from django.urls import path
from . import views

# write your urls here

urlpatterns = [
    path('initiate/', views.InitiatePaymentView.as_view(), name='payment-initiate'),
    path('verify/', views.VerifyPaymentView.as_view(), name='payment-verify'),
    path('webhook/', views.PaystackWebhookView.as_view(), name='payment-webhook'),
    path('history/', views.PaymentHistoryView.as_view(), name='payment-history'),
    path('receipt/<str:receipt_number>/', views.PaymentReceiptView.as_view(), name='payment-receipt'),
]
