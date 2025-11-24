def get_response(message: str, **kwargs):
    return {
        "message": message,
        **kwargs,
    }
