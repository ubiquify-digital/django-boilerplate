import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from svix.webhooks import Webhook

from clerk.utils import verify_webhook_signature

User = get_user_model()
logger = logging.getLogger(__name__)


class ClerkWebhookView(APIView):
    """
    Handle Clerk webhook events.
    Supported events:
    - user.created
    - user.updated
    - user.deleted
    - session.created
    - session.ended
    """
    
    permission_classes = [AllowAny]
    authentication_classes = []  # Webhooks don't use standard authentication
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Override dispatch to apply csrf_exempt."""
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Handle POST requests from Clerk webhooks."""

        # Get the signature from headers (Clerk uses svix-signature header)
        svix_id = request.headers.get("svix-id")
        svix_timestamp = request.headers.get("svix-timestamp")
        svix_signature = request.headers.get("svix-signature")
        if not svix_id or not svix_timestamp or not svix_signature:
            logger.warning("Webhook request missing svix headers")
            return JsonResponse({
                "error": "Missing svix headers",
            }, status=401)

        # Get the raw body
        try:
            payload_body = request.body.decode("utf-8")
        except UnicodeDecodeError:
            logger.error("Webhook request has invalid payload encoding")
            return JsonResponse({"error": "Invalid payload encoding"}, status=400)

        logger.info(f"Payload body: {payload_body}")
        logger.info(f"Signature: {svix_signature}")

        try:
            webhook = Webhook(settings.CLERK_WEBHOOK_SECRET)
            webhook.verify(payload_body, {
                "svix-id": svix_id,
                "svix-timestamp": svix_timestamp,
                "svix-signature": svix_signature,
            })
        except Exception as e:
            logger.exception(f"Error verifying webhook: {str(e)}")
            return JsonResponse({"error": str(e)}, status=401)

        try:
            data = json.loads(payload_body)
            event_type = data.get("type")
            event_data = data.get("data", {})

            # Handle different event types
            handler_map = {
                "user.created": self.handle_user_created,
                "user.updated": self.handle_user_updated,
                "user.deleted": self.handle_user_deleted,
                "session.created": self.handle_session_created,
                "session.ended": self.handle_session_ended,
            }

            handler = handler_map.get(event_type)
            if handler:
                handler(event_data)
            else:
                logger.info(f"Unhandled webhook event: {event_type}")

            return JsonResponse({"status": "success"})

        except json.JSONDecodeError:
            logger.error("Webhook request has invalid JSON")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.exception(f"Error processing webhook: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    def handle_user_created(self, data):
        """
        Handle user.created webhook event.
        Create a new user in Django when a user is created in Clerk.
        """
        clerk_user_id = data.get("id")
        email_addresses = data.get("email_addresses", [])
        primary_email = next(
            (email.get("email_address") for email in email_addresses 
             if email.get("id") == data.get("primary_email_address_id")),
            email_addresses[0].get("email_address") if email_addresses else None,
        )

        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")

        if not clerk_user_id or not primary_email:
            logger.warning("user.created event missing required fields")
            return

        # Check if user already exists
        user, created = User.objects.get_or_create(
            clerk_user_id=clerk_user_id,
            defaults={
                "email": primary_email,
                "first_name": first_name,
                "last_name": last_name,
                "is_email_verified": True,
                "is_active": True,
            },
        )

        if not created:
            # Update existing user
            user.email = primary_email
            user.first_name = first_name
            user.last_name = last_name
            user.is_email_verified = True
            user.is_active = True
            user.save()
            logger.info(f"Updated user {user.email} from webhook")

    def handle_user_updated(self, data):
        """
        Handle user.updated webhook event.
        Update user information when a user is updated in Clerk.
        """
        clerk_user_id = data.get("id")
        if not clerk_user_id:
            logger.warning("user.updated event missing user ID")
            return

        try:
            user = User.objects.get(clerk_user_id=clerk_user_id)
        except User.DoesNotExist:
            # If user doesn't exist, create it
            self.handle_user_created(data)
            return

        # Update user fields
        email_addresses = data.get("email_addresses", [])
        primary_email = next(
            (email.get("email_address") for email in email_addresses 
             if email.get("id") == data.get("primary_email_address_id")),
            email_addresses[0].get("email_address") if email_addresses else None,
        )

        if primary_email:
            user.email = primary_email

        if data.get("first_name"):
            user.first_name = data.get("first_name")
        if data.get("last_name"):
            user.last_name = data.get("last_name")

        # Update email verification status
        if primary_email:
            user.is_email_verified = True

        user.save()
        logger.info(f"Updated user {user.email} from webhook")

    def handle_user_deleted(self, data):
        """
        Handle user.deleted webhook event.
        Deactivate user when a user is deleted in Clerk.
        """
        clerk_user_id = data.get("id")
        if not clerk_user_id:
            logger.warning("user.deleted event missing user ID")
            return

        try:
            user = User.objects.get(clerk_user_id=clerk_user_id)
            # Deactivate instead of deleting to preserve data
            user.is_active = False
            user.save()
            logger.info(f"Deactivated user {user.email} from webhook")
        except User.DoesNotExist:
            logger.warning(f"User with clerk_user_id {clerk_user_id} not found for deletion")

    def handle_session_created(self, data):
        """
        Handle session.created webhook event.
        Optional: Track active sessions.
        """
        # You can implement session tracking here if needed
        logger.debug(f"Session created: {data.get('id')}")

    def handle_session_ended(self, data):
        """
        Handle session.ended webhook event.
        Optional: Clean up session data.
        """
        # You can implement session cleanup here if needed
        logger.debug(f"Session ended: {data.get('id')}")

