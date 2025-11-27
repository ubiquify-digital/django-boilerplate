import logging
import inngest

# Create an Inngest client
inngest_client = inngest.Inngest(
    app_id="django_boilerplate",
    logger=logging.getLogger("django"),
)

