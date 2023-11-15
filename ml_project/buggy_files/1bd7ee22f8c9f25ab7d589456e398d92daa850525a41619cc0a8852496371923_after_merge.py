    def run_on(*, event: str):
        """A decorator to store and link a callback to an event."""

        def decorator(callback):
            RTMClient.on(event=event, callback=callback)
            return callback

        return decorator