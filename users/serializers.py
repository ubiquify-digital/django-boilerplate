from django.contrib.auth import authenticate
from rest_framework import serializers

from common.mixin import CamelSnakeMixin
from users.models import UserAccount


class SignInSerializer(CamelSnakeMixin, serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError({"error": "Invalid credentials"})

        if not user.is_email_verified:
            raise serializers.ValidationError(
                {"error": "Email not verified, please verify your email first."}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"error": "Account is not active, please contact support."}
            )

        attrs["user"] = user
        return attrs


class UserAccountSerializer(CamelSnakeMixin, serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ["first_name", "last_name", "email", "is_superuser"]


class SignInResponseSerializer(CamelSnakeMixin, serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserAccountSerializer()


class SignUpSerializer(CamelSnakeMixin, serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)

    def validate(self, attrs):
        email = attrs.get("email")
        if email and UserAccount.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"error": "User with this email already exists."}
            )

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"error": "Passwords do not match."})
        return attrs


class VerifyOTPSerializer(CamelSnakeMixin, serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=8)


class ResendOTPSerializer(CamelSnakeMixin, serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")
        if not email:
            raise serializers.ValidationError({"error": "Email is required."})
        try:
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            raise serializers.ValidationError(
                {"error": "User with this email does not exist."}
            ) from None
        if user.is_email_verified:
            raise serializers.ValidationError({"error": "Email is already verified."})
        attrs["user"] = user
        return attrs
