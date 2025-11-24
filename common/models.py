import uuid

from django.db import models


class NormalizedEmailField(models.EmailField):
    """
    Email field that automatically normalizes email addresses by:
    - Converting to lowercase
    - Stripping whitespace
    """

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value:
            value = value.strip().lower()
            setattr(model_instance, self.attname, value)
        return super().pre_save(model_instance, add)


class TimeStampModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseContactForm(TimeStampModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = NormalizedEmailField(max_length=255)

    sign_up_for_newsletter = models.BooleanField(default=False)

    class Meta:
        abstract = True
