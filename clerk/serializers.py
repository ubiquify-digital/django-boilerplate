from rest_framework import serializers

from common.mixin import CamelSnakeMixin
from users.models import UserAccount


class UserAccountSerializer(CamelSnakeMixin, serializers.ModelSerializer):
    """Serializer for UserAccount model."""
    
    class Meta:
        model = UserAccount
        fields = ["first_name", "last_name", "email", "is_superuser"]


class VerifySessionResponseSerializer(CamelSnakeMixin, serializers.Serializer):
    """Serializer for verify session response."""
    
    authenticated = serializers.BooleanField()
    user = UserAccountSerializer(required=False)
    message = serializers.CharField(required=False)


class UserInfoResponseSerializer(CamelSnakeMixin, serializers.Serializer):
    """Serializer for user info response."""
    
    user = UserAccountSerializer()

