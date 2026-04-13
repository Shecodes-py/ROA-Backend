from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Welcome to the Authentication System")

def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('book_service')
    return HttpResponse("Login Page")

def logout_view(request):
    logout(request)
    return redirect('index')

def register_view(request):
    if request.method == "POST":
        # Registration logic here
        pass
    return HttpResponse("Register Page")
