from django.shortcuts import render
from django.views.generic import ListView
from rest_framework import generics
from .models import Service
from .serializers import ServiceSerializer

# Create your views here.

class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ServiceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

