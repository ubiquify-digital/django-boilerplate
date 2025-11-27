import logging

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from clerk.authentication import ClerkAuthentication
from clerk.serializers import (
    UserInfoResponseSerializer,
    VerifySessionResponseSerializer,
)

logger = logging.getLogger(__name__)


class ClerkVerifySessionView(APIView):
    """
    Verify Clerk session and return user information.
    This endpoint can be used to verify if a user is authenticated via Clerk.
    """
    
    authentication_classes = []  # Disable automatic authentication
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Handle GET request for session verification."""
        return self._verify_session(request)
    
    def post(self, request):
        """Handle POST request for session verification."""
        return self._verify_session(request)
    
    def _verify_session(self, request):
        """Common logic for verifying session."""
        auth = ClerkAuthentication()
        result = auth.authenticate(request)

        if result is None:
            return Response(
                {
                    "authenticated": False,
                    "message": "No valid Clerk session found"
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user, token = result
        serializer = VerifySessionResponseSerializer({
            "authenticated": True,
            "user": user
        })

        return Response(serializer.data, status=status.HTTP_200_OK)


class ClerkUserInfoView(APIView):
    """
    Get current authenticated user information via Clerk.
    This endpoint allows unauthenticated access but will return an error
    if the user is not authenticated.
    """
    
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get authenticated user information."""
        # Manually authenticate if a token is present (optional authentication)
        auth = ClerkAuthentication()
        
        # Check if token exists first
        token = auth.get_token(request)
        logger.debug(f"Token present: {bool(token)}, Headers: {dict(request.headers)}")
        
        if not token:
            logger.debug("No token found in request")
            return Response(
                {"error": "User not authenticated", "message": "No token provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        try:
            result = auth.authenticate(request)
            if result is None:
                logger.debug("Authentication returned None")
                return Response(
                    {"error": "User not authenticated", "message": "Authentication failed"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            user, token = result
            logger.debug(f"User authenticated: {user.email}")
        except AuthenticationFailed as e:
            # Handle authentication-specific errors
            error_message = str(e)
            logger.warning(f"Authentication failed: {error_message}")
            return Response(
                {"error": "User not authenticated", "message": error_message},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            # Handle unexpected errors
            logger.exception(f"Unexpected error during authentication: {str(e)}")
            return Response(
                {"error": "User not authenticated", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        serializer = UserInfoResponseSerializer({"user": user})
        return Response(serializer.data, status=status.HTTP_200_OK)

