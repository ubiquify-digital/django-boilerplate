import random
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.models import UserAccount
from users.serializers import (
    ResendOTPSerializer,
    SignInResponseSerializer,
    SignInSerializer,
    SignUpSerializer,
    UserAccountSerializer,
    VerifyOTPSerializer,
)
from users.tasks import send_otp_email


class SignInView(TokenObtainPairView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        serializer = self.get_serializer(data=serializer.validated_data)
        serializer.is_valid(raise_exception=True)

        tokens = serializer.validated_data

        response_serializer = SignInResponseSerializer(
            {
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user": user,
            }
        )
        response_data = response_serializer.data
        response = Response()
        response.data = response_data
        response.set_cookie(
            "access",
            tokens["access"],
            httponly=True,
            secure=True,
            samesite="Strict",
        )
        response.set_cookie(
            "refresh",
            tokens["refresh"],
            httponly=True,
            secure=True,
            samesite="Strict",
        )
        return response


class RefreshTokenView(TokenRefreshView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = serializer.validated_data

        # Get the user from the refresh token
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh_token = RefreshToken(tokens["refresh"])
        user = refresh_token.payload.get("user_id")
        from users.models import UserAccount

        user = UserAccount.objects.get(id=user)

        response_serializer = SignInResponseSerializer(
            {
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user": user,
            }
        )
        response_data = response_serializer.data
        response = Response()
        response.data = response_data
        response.set_cookie(
            "access",
            tokens["access"],
            httponly=True,
            secure=True,
            samesite="Strict",
        )
        response.set_cookie(
            "refresh",
            tokens["refresh"],
            httponly=True,
            secure=True,
            samesite="Strict",
        )
        return response


class SignUpView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = SignUpSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        first_name = serializer.validated_data["first_name"]
        last_name = serializer.validated_data["last_name"]

        # Create user (inactive until OTP is verified)
        user = UserAccount.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False,  # User will be activated after OTP verification
        )

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_expiry = timezone.now() + timedelta(minutes=10)
        user.otp_sent_at = timezone.now()
        user.save()

        # Send OTP email asynchronously using Celery
        send_otp_email.delay(email, otp)

        return Response(
            {
                "message": "User created successfully. Please check your email for OTP verification.",
                "email": email,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if OTP exists and is valid
        if not user.otp:
            return Response(
                {"error": "No OTP found. Please request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if OTP is expired
        if user.otp_expiry and timezone.now() > user.otp_expiry:
            user.otp = None
            user.otp_expiry = None
            user.save()
            return Response(
                {"error": "OTP has expired. Please request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify OTP
        if user.otp != otp:
            return Response(
                {"error": "Invalid OTP. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # OTP is valid - activate user and mark email as verified
        user.is_active = True
        user.is_email_verified = True
        user.email_verified_at = timezone.now()
        user.otp = None
        user.otp_expiry = None
        user.save()

        return Response(
            {
                "message": "Email verified successfully. Your account is now active.",
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )


class UserInfoView(APIView):
    """View for retrieving authenticated user information"""

    serializer_class = UserAccountSerializer

    def get(self, request):
        """Get authenticated user information"""
        serializer = self.serializer_class(request.user)
        return Response(
            {
                "message": "User information retrieved successfully",
                "user": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ResendOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = ResendOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Generate new OTP
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_expiry = timezone.now() + timedelta(
            minutes=10
        )  # OTP valid for 10 minutes
        user.otp_sent_at = timezone.now()
        user.save()

        # Send OTP email asynchronously using Celery
        send_otp_email.delay(user.email, otp)
        return Response(
            {
                "message": "OTP resent successfully",
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )
