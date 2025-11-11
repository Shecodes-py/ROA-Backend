from django.urls import path
from .views import *

urlpatterns = [
    # Service booking URLs
    path('services/', ServiceListView.as_view(), name='service-list'),
]