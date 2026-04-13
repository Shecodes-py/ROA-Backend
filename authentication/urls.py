from django.urls import path
from .views import *

urlpatterns = [
    # Authentication URLs
    path('', index, name='index'),
    path('login/', LoginViewSet.as_view({'post': 'create'}), name='login'),
    path('register/', RegisterViewSet.as_view({'post': 'create'}), name='register'),
]
