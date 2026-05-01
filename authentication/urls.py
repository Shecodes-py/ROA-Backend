from django.urls import path
from .views import *

# write your urls here
urlpatterns = [
    # Auth
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),

    # User
    path("profile/", ProfileView.as_view(), name="profile"),

    # blank
    path("", index, name="home"),

    path('password-reset/request/', RequestOTPView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', ResetPasswordView.as_view(), name='password_reset_confirm'),

]