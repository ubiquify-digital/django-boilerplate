import hashlib
import logging
import hmac
import time


from django.conf import settings

logger = logging.getLogger(__name__)


def verify_webhook_signature(payload_body, signature_header):
    """
    Verify the webhook signature from Clerk using Svix format.
    Clerk uses Svix for webhooks, which sends signatures in the format:
    v1,timestamp,signature (or multiple signatures separated by spaces)
    
    Args:
        payload_body: The raw request body as a string
        signature_header: The svix-signature header value
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    logger.info(f"Verifying signature: {signature_header}")
    logger.info(f"Payload body: {payload_body}")
    logger.info(f"CLERK_WEBHOOK_SECRET: {settings.CLERK_WEBHOOK_SECRET}")
    if not settings.CLERK_WEBHOOK_SECRET:
        logger.warning("CLERK_WEBHOOK_SECRET not configured, skipping signature verification")
        return False

    if not signature_header:
        logger.warning("Webhook request missing signature header")
        return False

    # Parse the svix-signature header
    # Format: v1,timestamp1,signature1 v1,timestamp2,signature2 ...
    signatures = signature_header.split()

    logger.info(f"Signatures: {signatures}")
    for signature_entry in signatures:
        try:
            # Parse each signature entry: v1,timestamp,signature
            parts = signature_entry.split(',')
            if len(parts) != 3 or parts[0] != 'v1':
                continue
            
            timestamp = parts[1]
            signature = parts[2]
            
            # Create the signed payload: timestamp.payload_body
            signed_payload = f"{timestamp}.{payload_body}"
            
            # Create HMAC signature
            expected_signature = hmac.new(
                settings.CLERK_WEBHOOK_SECRET.encode("utf-8"),
                signed_payload.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            
            # Compare signatures using constant-time comparison
            if hmac.compare_digest(expected_signature, signature):
                logger.info(f"Signature matches: {expected_signature} == {signature}")
                # Optional: Verify timestamp is within acceptable range (e.g., 5 minutes)
                try:
                    timestamp_int = int(timestamp)
                    current_time = int(time.time())
                    # Allow 5 minutes tolerance
                    if abs(current_time - timestamp_int) < 300:
                        logger.info(f"Timestamp is within acceptable range: {timestamp_int} == {current_time}")
                        return True
                except ValueError:
                    # If timestamp parsing fails, still accept if signature matches
                    logger.info(f"Timestamp parsing failed, still accepting if signature matches")
                    return True
                    
        except (ValueError, IndexError):
            # If parsing fails, try next signature
            logger.info(f"Parsing failed, trying next signature")
            continue
    
    logger.info(f"No signature matches found")
    return False

