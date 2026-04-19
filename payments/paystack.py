"""
A thin wrapper around the Paystack API.
All Paystack HTTP calls go through this class — keeps views clean.
"""
import hmac
import hashlib
import requests
from django.conf import settings


PAYSTACK_BASE_URL = "https://api.paystack.co"


class PaystackService:

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def initialize_transaction(self, *, email: str, amount_kobo: int, reference: str, metadata: dict = None):
        """
        Call Paystack's /transaction/initialize endpoint.
        Returns the authorization_url to redirect the user to.

        amount_kobo: amount in kobo (NGN × 100)
        """
        payload = {
            "email": email,
            "amount": amount_kobo,
            "reference": reference,
            "currency": "NGN",
            "metadata": metadata or {},
            "callback_url": settings.PAYSTACK_CALLBACK_URL,
        }
        response = requests.post(
            f"{PAYSTACK_BASE_URL}/transaction/initialize",
            json=payload,
            headers=self.headers,
            timeout=30,
        )
        return response.json()

    def verify_transaction(self, reference: str):
        """
        Verify a transaction by its reference.
        Returns the full Paystack response dict.
        """
        response = requests.get(
            f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}",
            headers=self.headers,
            timeout=30,
        )
        return response.json()

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Validate that a webhook came from Paystack by checking the
        HMAC-SHA512 signature against your secret key.
        """
        computed = hmac.new(
            self.secret_key.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha512,
        ).hexdigest()
        return hmac.compare_digest(computed, signature)

    def list_transactions(self, per_page: int = 50, page: int = 1):
        response = requests.get(
            f"{PAYSTACK_BASE_URL}/transaction",
            headers=self.headers,
            params={"perPage": per_page, "page": page},
            timeout=30,
        )
        return response.json()