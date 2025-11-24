from .base import *

DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("DJANGO_EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = 587
EMAIL_HOST_USER = env("DJANGO_EMAIL_USER")
EMAIL_HOST_PASSWORD = env("DJANGO_EMAIL_PASSWORD")
EMAIL_USE_TLS = True

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": "/var/log/django_error.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

ENV = "production"

# Database-based sessions
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=False)  # Only send cookies over HTTPS (requires SSL)
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = "Lax"  # CSRF protection
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 2 weeks (default)
SESSION_SAVE_EVERY_REQUEST = False  # Only save session when modified
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Persist session after browser close

AWS_S3_SIGNATURE_VERSION = "s3v4"
