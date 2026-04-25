from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()

# Create your views here.
def index(request):
    return render(request, "index.html")

class RegisterView(generics.CreateAPIView):
    """
    Register a new user account.
    Returns the created user's basic profile.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    # @swagger_auto_schema(
    #     operation_summary="Register new user",
    #     operation_description="Create a new user account with email and password.",
    #     responses={
    #         201: openapi.Response("User created", RegisterSerializer),
    #         400: "Validation error",
    #     },
    #     tags=["Authentication"],
    # )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
 
        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email
        refresh["full_name"] = user.full_name
 
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,

        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    Obtain JWT access + refresh tokens.
    Returns tokens alongside user dashboard data.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="Login / obtain tokens",
        operation_description=(
            "Authenticate with email and password. "
            "Returns `access` (60 min) and `refresh` (7 days) tokens."
        ),
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # Update last_activity on login
        if response.status_code == 200:
            try:
                user = User.objects.get(email=request.data.get("email"))
                user.last_activity = timezone.now()
                user.save(update_fields=["last_activity"])
            except User.DoesNotExist:
                pass
        return response


class TokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_summary="Refresh access token",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """Blacklist the refresh token on logout."""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Logout",
        operation_description="Blacklist the refresh token so it can no longer be used.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={"refresh": openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        responses={205: "Logged out", 400: "Bad request"},
        tags=["Authentication"],
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

# I want to merge profile and dashboard into a single endpoint that returns all user info in one response.
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated user's full profile,
    including address and contact information.
    Contains profile completion, contact summary, and notification settings.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch"]
    
    def get_object(self):
        user = self.request.user
        user.last_activity = timezone.now()
        user.save(update_fields=["last_activity"])
        return user

    @swagger_auto_schema(
        operation_summary="Get my profile",
        tags=["Profile"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update my profile",
        operation_description="Partial update — only send the fields you want to change.",
        tags=["Profile"],
    )
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """Change the authenticated user's password."""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Change password",
        request_body=ChangePasswordSerializer,
        responses={200: "Password changed", 400: "Validation error"},
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)