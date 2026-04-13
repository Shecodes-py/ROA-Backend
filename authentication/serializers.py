from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds extra user data to the JWT token payload."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["full_name"] = user.full_name
        token["is_staff"] = user.is_staff
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Attach user info to the login response
        data["user"] = UserDashboardSerializer(self.user).data
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "email", "first_name", "last_name",
            "password", "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "address_line1", "address_line2",
            "city", "state", "postal_code", "country",
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    full_address = serializers.CharField(read_only=True)
    profile_completion = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "full_name",
            "avatar", "bio", "date_of_birth",
            "phone_number", "phone_verified",
            "address_line1", "address_line2", "city", "state",
            "postal_code", "country", "full_address",
            "notification_preference",
            "is_email_verified", "last_activity",
            "profile_completion", "date_joined",
        ]
        read_only_fields = [
            "id", "email", "phone_verified", "is_email_verified",
            "last_activity", "date_joined",
        ]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.calculate_profile_completion()
        return instance


class UserDashboardSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "avatar",
            "phone_number", "full_address",
            "notification_preference",
            "is_email_verified", "profile_completion",
            "last_activity", "date_joined",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={"input_type": "password"})
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    new_password_confirm = serializers.CharField(required=True, style={"input_type": "password"})

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password": "Passwords do not match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value