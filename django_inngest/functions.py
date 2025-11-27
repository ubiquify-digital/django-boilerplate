import inngest

from .client import inngest_client


# Create a simple hello world Inngest function
@inngest_client.create_function(
    fn_id="hello_world",
    # Event that triggers this function
    trigger=inngest.TriggerEvent(event="hello/world"),
)
def hello_world(ctx: inngest.Context) -> str:
    """
    A simple hello world function that prints a message.
    """
    name = ctx.event.data.get("name", "World")
    message = f"Hello, {name}!"
    print(message)
    return message

