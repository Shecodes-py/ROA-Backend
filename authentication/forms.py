from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service_name', 'date']