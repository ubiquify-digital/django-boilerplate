import json

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from jwt.algorithms import RSAAlgorithm
from rest_framework import authentication, exceptions

User = get_user_model()


class ClerkAuthentication(authentication.BaseAuthentication):
    """
    Clerk JWT token authentication backend for Django REST Framework.
    Verifies Clerk session tokens and authenticates users.
    """

    def authenticate(self, request):
        """
        Authenticate the request using Clerk session token.
        Token can be provided in:
        - Authorization header: "Bearer <token>"
        - Cookie: "clerk_session" or "__session"
        """
        token = self.get_token(request)

        if not token:
            return None

        try:
            # Verify and decode the Clerk token
            payload = self.verify_token(token)
            clerk_user_id = payload.get("sub")

            if not clerk_user_id:
                raise exceptions.AuthenticationFailed("Invalid token: missing user ID")

            # Get or create user from Clerk user ID
            user = self.get_or_create_user(clerk_user_id, payload)

            return (user, token)

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f"Invalid token: {str(e)}")
        except exceptions.AuthenticationFailed:
            raise
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Authentication failed: {str(e)}")

    def get_token(self, request):
        """Extract token from Authorization header or cookie."""
        # Check Authorization header first
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]

        # Check cookie
        return request.COOKIES.get("clerk_session") or request.COOKIES.get("__session")

    def get_clerk_domain(self):
        """
        Get the Clerk frontend API domain, stripping any protocol.
        """
        domain = settings.CLERK_FRONTEND_API
        if not domain:
            return None
        # Remove protocol if present
        domain = domain.replace("https://", "").replace("http://", "")
        # Remove trailing slash
        domain = domain.rstrip("/")
        return domain

    def verify_token(self, token):
        """
        Verify Clerk JWT token using Clerk's public key.
        Uses Clerk's JWKS endpoint to get the public key for verification.
        """
        clerk_domain = self.get_clerk_domain()
        if not clerk_domain:
            raise exceptions.AuthenticationFailed("CLERK_FRONTEND_API not configured")

        # Get Clerk's JWKS (JSON Web Key Set) to verify the token
        jwks_url = f"https://{clerk_domain}/.well-known/jwks.json"
        try:
            jwks_response = requests.get(jwks_url, timeout=5)
            jwks_response.raise_for_status()
            jwks = jwks_response.json()
        except requests.RequestException as e:
            raise exceptions.AuthenticationFailed(f"Failed to fetch JWKS: {str(e)}")

        # Decode header to get the key ID
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed("Invalid token format")

        if not kid:
            raise exceptions.AuthenticationFailed("Token missing key ID")

        # Find the matching key
        key = None
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                try:
                    key = RSAAlgorithm.from_jwk(json.dumps(jwk))
                    break
                except Exception:
                    continue

        if not key:
            raise exceptions.AuthenticationFailed("Unable to find appropriate key")

        # Verify and decode the token
        try:
            decoded = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=clerk_domain,
                issuer=f"https://{clerk_domain}",
            )
            return decoded
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f"Invalid token: {str(e)}")

    def get_or_create_user(self, clerk_user_id, payload):
        """
        Get or create a Django user from Clerk user ID.
        """
        try:
            user = User.objects.get(clerk_user_id=clerk_user_id)
            # Update user data from payload if needed
            self.update_user_from_payload(user, payload)
            return user
        except User.DoesNotExist:
            # Create new user from Clerk data
            return self.create_user_from_clerk(clerk_user_id, payload)

    def create_user_from_clerk(self, clerk_user_id, payload):
        """
        Create a new Django user from Clerk payload.
        """
        email = payload.get("email") or payload.get("primary_email_address")
        first_name = payload.get("first_name") or payload.get("given_name") or ""
        last_name = payload.get("last_name") or payload.get("family_name") or ""

        if not email:
            raise exceptions.AuthenticationFailed("Email not found in token")

        # Check if user with this email already exists
        try:
            user = User.objects.get(email=email)
            # Link Clerk ID to existing user
            user.clerk_user_id = clerk_user_id
            user.is_email_verified = True
            user.is_active = True
            user.save()
            return user
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                clerk_user_id=clerk_user_id,
                is_email_verified=True,
                is_active=True,
                password=None,  # No password needed for Clerk users
            )
            return user

    def update_user_from_payload(self, user, payload):
        """
        Update user information from Clerk payload if needed.
        """
        email = payload.get("email") or payload.get("primary_email_address")
        first_name = payload.get("first_name") or payload.get("given_name")
        last_name = payload.get("last_name") or payload.get("family_name")

        updated = False
        if email and user.email != email:
            user.email = email
            updated = True
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updated = True

        if updated:
            user.save()

