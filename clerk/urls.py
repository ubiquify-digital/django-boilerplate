from django.urls import path

from clerk.views import ClerkUserInfoView, ClerkVerifySessionView
from clerk.webhook import ClerkWebhookView

app_name = "clerk"

urlpatterns = [
    path("verify-session/", ClerkVerifySessionView.as_view(), name="verify-session"),
    path("user-info/", ClerkUserInfoView.as_view(), name="user-info"),
    path("webhook/", ClerkWebhookView.as_view(), name="webhook"),
]

