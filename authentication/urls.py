from django.urls import path
from . import views

# write your urls here
urlpatterns = [
    # Auth
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("token/refresh/", views.TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),

    # User
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
]