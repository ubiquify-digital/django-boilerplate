import os


def dynamic_upload_path(instance, filename):
    """Dynamic path for photo uploads based on model type."""
    return os.path.join(f"{instance.__class__.__name__.lower()}_files/", filename)


def dynamic_company_logo_upload_path(instance, filename):
    """Dynamic path for company logo uploads based on company name."""
    return os.path.join(f"company_logos/{instance.name}/", filename)

