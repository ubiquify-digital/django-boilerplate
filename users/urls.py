from django.urls import path

from users.views import (
    RefreshTokenView,
    ResendOTPView,
    SignInView,
    SignUpView,
    UserInfoView,
    VerifyOTPView,
)

urlpatterns = [
    path("sign-in/", SignInView.as_view(), name="sign-in"),
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    # Resend OTP
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    # Verify OTP
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    # Refresh Token
    path("refresh-token/", RefreshTokenView.as_view(), name="refresh-token"),
    # User Info
    path("user-info/", UserInfoView.as_view(), name="user-info"),
]
