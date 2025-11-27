import inngest
import inngest.django

from .client import inngest_client
from .functions import hello_world


# List of all active Inngest functions
active_inngest_functions = [
    hello_world,
]

# Create the Inngest serve endpoint
inngest_view_path = inngest.django.serve(inngest_client, active_inngest_functions)

