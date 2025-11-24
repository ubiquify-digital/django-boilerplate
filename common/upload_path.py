import os


def dynamic_document_upload_path(instance, filename):
    """Dynamic path for document uploads based on document type."""
    instance_name = instance.__class__.__name__.lower()
    if instance_name == "agency":
        instance_name = "agency/signup_agreements"
    if hasattr(instance, "name"):
        instance_name = f"{instance_name}/{instance.name}"
    return os.path.join(f"{instance_name}/", filename)
