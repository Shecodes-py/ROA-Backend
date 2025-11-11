from django.contrib import requests
from .models import Booking 
from django.shortcuts import redirect

def initiate_payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    payload = {
        "email": request.user.email,
        "amount": 5000 * 100,  # amount in kobo
    }
    headers = {"Authorization": "Bearer YOUR_PAYSTACK_SECRET_KEY"}
    response = requests.post("https://api.paystack.co/transaction/initialize", json=payload, headers=headers)
    return redirect(response.json()['data']['authorization_url'])