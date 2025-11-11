from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import BookingForm

# Create your views here.
def index(request):
    return render(request, 'auth/index.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('book_service')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def register_view(request):
    if request.method == "POST":
        # Registration logic here
        pass
    return render(request, 'register.html')
