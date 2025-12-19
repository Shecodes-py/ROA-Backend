from django.urls import path
from .views import *

urlpatterns = [
    # Service booking URLs
    path('services_type/', ServiceListView.as_view(), name='service-list'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    
]