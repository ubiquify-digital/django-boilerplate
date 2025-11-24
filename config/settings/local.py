from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

INSTALLED_APPS += []

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("DJANGO_EMAIL_HOST")
EMAIL_PORT = env("DJANGO_EMAIL_PORT", default=587)  # type: ignore
EMAIL_USE_TLS = env("DJANGO_EMAIL_USE_TLS", default=True)  # type: ignore
EMAIL_HOST_USER = env("DJANGO_EMAIL_USER", default="Django <test@django.com>")  # e.g. yourname@gmail.com
EMAIL_HOST_PASSWORD = env("DJANGO_EMAIL_PASSWORD", default="")

ENV = "local"

AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="http://localhost:4566")  # type: ignore
AWS_S3_USE_SSL = env("AWS_S3_USE_SSL", default=False)  # type: ignore
AWS_S3_VERIFY = env("AWS_S3_VERIFY", default=False)  # type: ignore
