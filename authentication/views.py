from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


# Create your views here.
def index(request):
    return HttpResponse("Welcome to the Authentication System")

class LoginViewSet(viewsets.ViewSet):
    """API endpoint for user login."""
    permission_classes = [AllowAny]

    def create(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class RegisterViewSet(viewsets.ViewSet):
    """API endpoint for user registration."""
    permission_classes = [AllowAny]

    def create(self, request):
    
        if request.method == "POST":
                email = request.data.get('email')
                password = request.data.get('password')
                # Additional fields can be handled here
    
                # Basic validation (e.g., check if email already exists) can be added here
        # Registration logic here (e.g., validate data, create user)
        return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
